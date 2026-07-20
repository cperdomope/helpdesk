from actions import crear_ticket, listar_tickets, asignar_ticket
from database import SessionLocal
from models import Usuario


def login() -> Usuario | None:
    db = SessionLocal()
    username = input("Usuario: ")
    usuario = db.query(Usuario).filter_by(username=username).first()

    if not usuario:
        print("\n❌ Usuario no encontrado.\n")
        db.close()
        return None

    if not usuario.activo:
        print("\n❌ Usuario inactivo.\n")
        db.close()
        return None

    db.close()
    return usuario


def menu() -> None:
    print("===== BIENVENIDO AL HELP DESK =====")
    usuario_actual = login()
    if usuario_actual is None:
        return

    rol = usuario_actual.rol

    while True:
        print(f"\n===== HELP DESK ({usuario_actual}) =====")
        if rol == "usuario":
            print("1. Crear ticket")
            print("2. Listar tickets")
            print("3. Salir")
        else:
            print("1. Listar tickets")
            print("2. Asignar/actualizar ticket")
            print("3. Salir")

        opcion = input("Elige una opción: ")

        if rol == "usuario":
            if opcion == "1":
                crear_ticket(usuario_actual)
            elif opcion == "2":
                listar_tickets()
            elif opcion == "3":
                print("\n👋 Saliendo del sistema.")
                break
            else:
                print("\n⚠️  Opción no válida.\n")
        else:
            if opcion == "1":
                listar_tickets()
            elif opcion == "2":
                asignar_ticket(usuario_actual)
            elif opcion == "3":
                print("\n👋 Saliendo del sistema.")
                break
            else:
                print("\n⚠️  Opción no válida.\n")


if __name__ == "__main__":
    menu()
