from database import SessionLocal, init_db
from models import Usuario

# Crea las tablas en MySQL si aún no existen (no borra las que ya existen)
init_db()

db = SessionLocal()

username = "cperdomo"
usuario_existente = db.query(Usuario).filter_by(username=username).first()

if usuario_existente:
    print("El usuario ya existe con id:", usuario_existente.id)
else:
    nuevo_usuario = Usuario(
        username=username,
        nombre="Charles Perdomo",
        email="charles@helpdesk.local",
        rol="usuario",
    )
    nuevo_usuario.set_password("clave123")

    db.add(nuevo_usuario)
    db.commit()
    print("Usuario creado con id:", nuevo_usuario.id)
