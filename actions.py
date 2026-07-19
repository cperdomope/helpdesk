from models import nuevo_ticket

tickets: list[dict] = []
contador_id: int = 1


class TicketYaResueltoError(Exception):
    """Se lanza cuando se intenta modificar un ticket que ya está resuelto."""
    pass


def crear_ticket() -> None:
    global contador_id

    usuario = input("Ingrese el nombre del usuario: ")
    asunto = input("Asunto del problema: ")
    categoria = input("Categoría (hardware/software/red): ")
    prioridad = input("Ingrese la prioridad del ticket (alta/media/baja): ")

    ticket = nuevo_ticket(contador_id, usuario, asunto, categoria, prioridad)
    tickets.append(ticket)
    contador_id += 1

    print(f"\n✅ Ticket #{ticket['id']} creado con éxito.\n")


def listar_tickets() -> None:
    if not tickets:
        print("\n⚠️  No hay tickets registrados.\n")
        return

    print("\n--- Lista de Tickets ---")
    for t in tickets:
        print(f"#{t['id']} | Usuario: {t['usuario']} | Asunto: {t['asunto']} | Estado: {t['estado']} | Prioridad: {t['prioridad']}")
    print()


def asignar_ticket() -> None:
    if not tickets:
        print("\n⚠️  No hay tickets registrados.\n")
        return

    listar_tickets()
    id_buscado = int(input("¿Qué número de ticket deseas actualizar? "))

    for t in tickets:
        if t["id"] == id_buscado:
            try:
                if t["estado"] == "resuelto":
                    raise TicketYaResueltoError(
                        f"El ticket #{t['id']} ya está resuelto y no puede modificarse.")

                nuevo_estado = input(
                    "Ingrese el nuevo estado (en progreso/resuelto): ")
                t["estado"] = nuevo_estado
                print(
                    f"\n✅ Ticket #{t['id']} actualizado a estado '{nuevo_estado}' con éxito.\n")
            except TicketYaResueltoError as error:
                print(f"\n⚠️  {error}\n")
            return

    print(f"\n❌ No se encontró un ticket con el ID #{id_buscado}.\n")
