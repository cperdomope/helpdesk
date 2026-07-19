from actions import crear_ticket, listar_tickets, asignar_ticket
from models import Cliente, Tecnico


def menu() -> None:
    print("===== BIENVENIDO AL HELP DESK =====")
    nombre = input("Ingresa tu nombre: ")
    correo = input("Ingresa tu correo: ")
    rol = input("¿Cuál es tu rol? (cliente/tecnico): ").strip().lower()

    if rol == "cliente":
        usuario_actual = Cliente(nombre, correo)
    elif rol == "tecnico":
        usuario_actual = Tecnico(nombre, correo)
    else:
        print("\n❌ Rol no válido. Cerrando el sistema.\n")
        return

    while True:
        print(f"\n===== HELP DESK ({usuario_actual}) =====")
        if rol == "cliente":
            print("1. Crear ticket")
            print("2. Listar tickets")
            print("3. Salir")
        else:
            print("1. Listar tickets")
            print("2. Asignar/actualizar ticket")
            print("3. Salir")

        opcion = input("Elige una opción: ")

        if rol == "cliente":
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
