tickets = []
contador_id = 1


def crear_ticket():
    global contador_id

    usuario = input("Ingrese el nombre del usuario: ")
    asunto = input("Asunto del problema: ")
    categoria = input("Categoría (hardware/software/red): ")
    prioridad = input("Ingrese la prioridad del ticket (alta/media/baja): ")

    ticket = {
        "id": contador_id,
        "usuario": usuario,
        "asunto": asunto,
        "categoria": categoria,
        "estado": "abierto",
        "prioridad": prioridad,
    }

    tickets.append(ticket)
    contador_id += 1
    print(f"\n✅Ticket #{ticket['id']} creado con éxito.\n")


def listar_tickets():
    if not tickets:
        print("\n⚠️No hay tickets registrados.\n")
        return

    print("\n---Lista de Tickets---")
    for t in tickets:
        print(
            f"#{t['id']} | Usuario: {t['usuario']} | Asunto: {t['asunto']} | Categoría: {t['categoria']} | Estado: {t['estado']} | Prioridad: {t['prioridad']}"
        )


def asignar_ticket():
    if not tickets:
        print("\n⚠️No hay tickets registrados.\n")
        return

    listar_tickets()
    id_buscado = int(input("¿Qué número de ticket deseas actualizar?: "))

    for t in tickets:
        if t["id"] == id_buscado:
            if t["estado"] == "resuelto":
                print(
                    f"\n⚠️ El ticket #{id_buscado} ya está resuelto, no se puede reasignar.\n"
                )
                return
            nuevo_estado = input(
                "Ingrese el nuevo estado del ticket (en progreso/resuelto): "
            )
            t["estado"] = nuevo_estado
            print(
                f"\n✅ Ticket #{t['id']} actualizado a estado '{nuevo_estado}' con éxito.\n"
            )
            return

    print(f"\n❌ No se encontró un ticket con el ID #{id_buscado}.\n")


def menu():
    while True:
        print("\n---HELP DESK---")
        print("1. Crear ticket")
        print("2. Listar tickets")
        print("3. Asignar/Actualizar ticket")
        print("4. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            crear_ticket()
        elif opcion == "2":
            listar_tickets()
        elif opcion == "3":
            asignar_ticket()
        elif opcion == "4":
            print("\n👋 Saliendo del sistema de tickets.\n")
            break
        else:
            print("\n❌ Opción inválida, por favor intente nuevamente.\n")


menu()
