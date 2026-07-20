from database import SessionLocal
from models import Usuario, Ticket


def crear_ticket(usuario_actual: Usuario) -> None:
    db = SessionLocal()

    titulo = input("Asunto del problema: ")
    descripcion = input("Descripción detallada: ")
    categoria = input("Categoría (hardware/software/red): ")
    prioridad = input("Ingrese la prioridad del ticket (alta/media/baja): ")

    nuevo_ticket = Ticket(
        titulo=titulo,
        descripcion=descripcion,
        categoria=categoria,
        prioridad=prioridad,
        estado="abierto",
        creador_id=usuario_actual.id
    )

    db.add(nuevo_ticket)
    db.commit()
    db.refresh(nuevo_ticket)

    print(f"\n✅ Ticket #{nuevo_ticket.id} creado correctamente.\n")
    db.close()


def listar_tickets() -> None:
    db = SessionLocal()
    tickets = db.query(Ticket).all()

    if not tickets:
        print("\n⚠️  No hay tickets registrados.\n")
        db.close()
        return

    print("\n--- Lista de Tickets ---")
    for t in tickets:
        print(f"#{t.id} | Creador: {t.creador.username} | Título: {t.titulo} | Estado: {t.estado} | Prioridad: {t.prioridad}")
    print()

    db.close()


def asignar_ticket(usuario_actual: Usuario) -> None:
    db = SessionLocal()
    tickets = db.query(Ticket).all()

    if not tickets:
        print("\n⚠️  No hay tickets registrados.\n")
        db.close()
        return

    print("\n--- Lista de Tickets ---")
    for t in tickets:
        print(f"#{t.id} | Creador: {t.creador.username} | Título: {t.titulo} | Estado: {t.estado} | Prioridad: {t.prioridad}")
    print()

    id_buscado = int(input("¿Qué número de ticket deseas actualizar? "))
    ticket = db.query(Ticket).filter_by(id=id_buscado).first()

    if not ticket:
        print(f"\n❌ No se encontró un ticket con el ID #{id_buscado}.\n")
        db.close()
        return

    if ticket.estado == "resuelto":
        print("\n⚠️  Este ticket ya está resuelto.\n")
        db.close()
        return

    nuevo_estado = input("Ingrese el nuevo estado (en_progreso/resuelto): ")
    ticket.estado = nuevo_estado
    ticket.tecnico_id = usuario_actual.id

    db.commit()
    print(f"\n✅ Ticket #{ticket.id} actualizado a '{nuevo_estado}'.\n")
    db.close()
