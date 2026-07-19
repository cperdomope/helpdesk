from actions import crear_ticket, listar_tickets, asignar_ticket


def menu() -> None:
    while True:
        print("===== HELP DESK =====")
        print("1. Crear ticket")
        print("2. Listar tickets")
        print("3. Asignar/actualizar ticket")
        print("4. Salir")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            crear_ticket()
        elif opcion == "2":
            listar_tickets()
        elif opcion == "3":
            asignar_ticket()
        elif opcion == "4":
            print("\n👋 Saliendo del sistema de tickets.")
            break
        else:
            print("\n⚠️  Opción no válida, intenta de nuevo.\n")


if __name__ == "__main__":
    menu()
