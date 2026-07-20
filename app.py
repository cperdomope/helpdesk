from functools import wraps
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from database import SessionLocal, init_db
from models import Usuario, Ticket, Comentario, HistorialTicket
from forms import TicketForm
from sqlalchemy import text
from flask import abort

app = Flask(__name__)
app.secret_key = "helpdesk-secret-key-change-in-production"


@app.template_filter('fecha_es')
def fecha_es(valor, con_hora=False):
    if not valor:
        return ""
    if con_hora:
        return valor.strftime('%d/%m/%Y %H:%M')
    return valor.strftime('%d/%m/%Y')


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Por favor, inicia sesion para continuar."


@login_manager.user_loader
def load_user(user_id):
    return SessionLocal.query(Usuario).get(int(user_id))


def rol_requerido(*roles):
    def decorador(f):
        @wraps(f)
        def funcion_envuelta(*args, **kwargs):
            if current_user.rol not in roles:
                abort(403)
            return f(*args, **kwargs)
        return funcion_envuelta
    return decorador


def registrar_historial(db, ticket, usuario, accion, detalle=None):
    h = HistorialTicket(ticket_id=ticket.id,
                        usuario_id=usuario.id, accion=accion, detalle=detalle)
    db.add(h)
    db.commit()


# ── Auth ────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        db = SessionLocal()
        user = db.query(Usuario).filter_by(username=username).first()
        if user and user.check_password(password) and user.activo:
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Credenciales incorrectas.", "error")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route('/health')
def health():
    try:
        SessionLocal.execute(text('SELECT 1'))
        return {'status': 'ok', 'db': 'connected'}, 200
    except Exception:
        return {'status': 'error', 'db': 'disconnected'}, 503


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ── Dashboard ───────────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    db = SessionLocal()
    user = current_user
    if user.es_admin:
        total = db.query(Ticket).count()
        abiertos = db.query(Ticket).filter_by(estado="abierto").count()
        en_progreso = db.query(Ticket).filter_by(estado="en_progreso").count()
        resueltos = db.query(Ticket).filter_by(estado="resuelto").count()
        tickets_recientes = db.query(Ticket).order_by(
            Ticket.fecha_creacion.desc()).limit(5).all()
        usuarios_count = db.query(Usuario).filter_by(activo=1).count()
    elif user.es_tecnico:
        mis_tickets = db.query(Ticket).filter_by(tecnico_id=user.id).all()
        total = len(mis_tickets)
        abiertos = sum(1 for t in mis_tickets if t.estado == "abierto")
        en_progreso = sum(1 for t in mis_tickets if t.estado == "en_progreso")
        resueltos = sum(1 for t in mis_tickets if t.estado == "resuelto")
        tickets_recientes = db.query(Ticket).filter(
            (Ticket.tecnico_id == user.id) | (Ticket.estado == "abierto")
        ).order_by(Ticket.fecha_creacion.desc()).limit(5).all()
        usuarios_count = None
    else:
        mis_tickets = db.query(Ticket).filter_by(creador_id=user.id).all()
        total = len(mis_tickets)
        abiertos = sum(1 for t in mis_tickets if t.estado == "abierto")
        en_progreso = sum(1 for t in mis_tickets if t.estado == "en_progreso")
        resueltos = sum(1 for t in mis_tickets if t.estado == "resuelto")
        tickets_recientes = db.query(Ticket).filter_by(creador_id=user.id).order_by(
            Ticket.fecha_creacion.desc()).limit(5).all()
        usuarios_count = None
    return render_template("dashboard.html",
                           total=total, abiertos=abiertos,
                           en_progreso=en_progreso, resueltos=resueltos,
                           tickets_recientes=tickets_recientes,
                           usuarios_count=usuarios_count)


# ── Tickets ─────────────────────────────────────────────────────────
@app.route("/tickets")
@login_required
def tickets():
    db = SessionLocal()
    user = current_user
    filtro_estado = request.args.get("estado", "")
    filtro_prioridad = request.args.get("prioridad", "")

    query = db.query(Ticket)
    if user.es_usuario:
        query = query.filter_by(creador_id=user.id)
    elif user.es_tecnico:
        query = query.filter((Ticket.tecnico_id == user.id)
                             | (Ticket.tecnico_id.is_(None)))

    if filtro_estado:
        query = query.filter_by(estado=filtro_estado)
    if filtro_prioridad:
        query = query.filter_by(prioridad=filtro_prioridad)

    tickets_list = query.order_by(Ticket.fecha_creacion.desc()).all()
    return render_template("tickets.html", tickets=tickets_list,
                           filtro_estado=filtro_estado, filtro_prioridad=filtro_prioridad)


@app.route("/tickets/crear", methods=["GET", "POST"])
@login_required
def crear_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        db = SessionLocal()
        t = Ticket(
            titulo=form.titulo.data.strip(),
            descripcion=form.descripcion.data.strip(),
            categoria=form.categoria.data,
            prioridad=form.prioridad.data,
            creador_id=current_user.id,
        )
        db.add(t)
        db.commit()
        registrar_historial(db, t, current_user, "Ticket creado",
                            f"Ticket #{t.id} creado por {current_user.username}")
        flash(f"Ticket #{t.id} creado correctamente.", "success")
        return redirect(url_for("ver_ticket", ticket_id=t.id))
    return render_template("crear_ticket.html", form=form)


@app.route("/tickets/<int:ticket_id>")
@login_required
def ver_ticket(ticket_id):
    db = SessionLocal()
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket:
        flash("Ticket no encontrado.", "error")
        return redirect(url_for("tickets"))
    if current_user.es_usuario and ticket.creador_id != current_user.id:
        flash("No tienes acceso a este ticket.", "error")
        return redirect(url_for("tickets"))
    tecnicos = db.query(Usuario).filter(Usuario.rol.in_(
        ["tecnico", "admin"]), Usuario.activo == 1).all()
    return render_template("ver_ticket.html", ticket=ticket, tecnicos=tecnicos)


@app.route("/tickets/<int:ticket_id>/comentar", methods=["POST"])
@login_required
def comentar(ticket_id):
    db = SessionLocal()
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket:
        flash("Ticket no encontrado.", "error")
        return redirect(url_for("tickets"))
    contenido = request.form["contenido"].strip()
    if contenido:
        c = Comentario(contenido=contenido, ticket_id=ticket.id,
                       usuario_id=current_user.id)
        db.add(c)
        ticket.fecha_actualizacion = datetime.now(timezone.utc)
        db.commit()
        registrar_historial(db, ticket, current_user,
                            "Comentario agregado", contenido[:100])
    return redirect(url_for("ver_ticket", ticket_id=ticket.id))


@app.route("/tickets/<int:ticket_id>/estado", methods=["POST"])
@login_required
def cambiar_estado(ticket_id):
    db = SessionLocal()
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket:
        flash("Ticket no encontrado.", "error")
        return redirect(url_for("tickets"))
    nuevo_estado = request.form["estado"]
    estado_anterior = ticket.estado
    ticket.estado = nuevo_estado
    ticket.fecha_actualizacion = datetime.now(timezone.utc)
    db.commit()
    registrar_historial(db, ticket, current_user, "Estado cambiado",
                        f"'{estado_anterior}' → '{nuevo_estado}'")
    flash(f"Ticket #{ticket.id} actualizado a '{nuevo_estado}'.", "success")
    return redirect(url_for("ver_ticket", ticket_id=ticket.id))


@app.route("/tickets/<int:ticket_id>/asignar", methods=["POST"])
@login_required
def asignar_ticket(ticket_id):
    if not current_user.es_admin:
        flash("Solo admins pueden asignar tickets.", "error")
        return redirect(url_for("tickets"))
    db = SessionLocal()
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket:
        flash("Ticket no encontrado.", "error")
        return redirect(url_for("tickets"))
    tecnico_id = request.form.get("tecnico_id")
    tecnico_anterior = ticket.tecnico
    if tecnico_id:
        ticket.tecnico_id = int(tecnico_id)
    else:
        ticket.tecnico_id = None
    ticket.fecha_actualizacion = datetime.now(timezone.utc)
    db.commit()
    nuevo_tecnico = db.query(Usuario).get(
        int(tecnico_id)) if tecnico_id else None
    nombre_anterior = tecnico_anterior.username if tecnico_anterior else "Ninguno"
    nombre_nuevo = nuevo_tecnico.username if nuevo_tecnico else "Ninguno"
    registrar_historial(db, ticket, current_user, "Tecnico asignado",
                        f"Tecnico: '{nombre_anterior}' → '{nombre_nuevo}'")
    flash(f"Ticket #{ticket.id} asignado correctamente.", "success")
    return redirect(url_for("ver_ticket", ticket_id=ticket.id))


# ── Admin: Usuarios ─────────────────────────────────────────────────
@app.route("/admin/usuarios")
@login_required
@rol_requerido('admin')
def admin_usuarios():
    db = SessionLocal()

    usuarios = db.query(Usuario).order_by(Usuario.id).all()
    return render_template("admin_usuarios.html", usuarios=usuarios)


@app.route("/admin/usuarios/crear", methods=["GET", "POST"])
@login_required
@rol_requerido('admin')
def admin_crear_usuario():

    flash("Acceso no autorizado.", "error")
    return redirect(url_for("dashboard"))
    if request.method == "POST":
        db = SessionLocal()
        username = request.form["username"].strip()
        if db.query(Usuario).filter_by(username=username).first():
            flash("El nombre de usuario ya existe.", "error")
            return redirect(url_for("admin_crear_usuario"))
        u = Usuario(
            username=username,
            nombre=request.form["nombre"].strip(),
            email=request.form["email"].strip(),
            rol=request.form["rol"],
        )
        u.set_password(request.form["password"])
        db.add(u)
        db.commit()
        flash(f"Usuario '{u.username}' creado.", "success")
        return redirect(url_for("admin_usuarios"))
    return render_template("admin_crear_usuario.html")


@app.route("/admin/usuarios/<int:user_id>/toggle", methods=["POST"])
@login_required
@rol_requerido('admin')
def admin_toggle_usuario(user_id):
    db = SessionLocal()
    u = db.query(Usuario).get(user_id)
    if u and u.id != current_user.id:
        u.activo = 0 if u.activo else 1
        db.commit()
        estado = "activado" if u.activo else "desactivado"
        flash(f"Usuario '{u.username}' {estado}.", "success")
    return redirect(url_for("admin_usuarios"))


if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    if not db.query(Usuario).filter_by(username="admin").first():
        admin = Usuario(username="admin", nombre="Administrador",
                        email="admin@helpdesk.local", rol="admin")
        admin.set_password("admin123")
        db.add(admin)
        db.commit()
        print("✅ Usuario admin creado (admin / admin123)")
    db.close()
    app.run(debug=True, port=5000)
