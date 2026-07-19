from models import Ticket, Cliente, Tecnico, Administrador, TicketYaResueltoError

tickets: list[Ticket] = []
contador_id: int = 1


def crear_ticket(cliente: Cliente) -> None:
    global contador_id

    asunto = input("Asunto del problema: ")
    categoria = input("Categoría (hardware/software/red): ")
    prioridad = input("Ingrese la prioridad del ticket (alta/media/baja): ")

    ticket = cliente.crear_ticket(contador_id, asunto, categoria, prioridad)
    tickets.append(ticket)
    contador_id += 1


def listar_tickets() -> None:
    if not tickets:
        print("\n⚠️  No hay tickets registrados.\n")
        return

    print("\n--- Lista de Tickets ---")
    for t in tickets:
        print(f"#{t.id} | Usuario: {t.usuario} | Asunto: {t.asunto} | Estado: {t.estado} | Prioridad: {t.prioridad}")
    print()


def asignar_ticket(tecnico: Tecnico) -> None:
    if not tickets:
        print("\n⚠️  No hay tickets registrados.\n")
        return

    listar_tickets()
    id_buscado = int(input("¿Qué número de ticket deseas actualizar? "))

    for t in tickets:
        if t.id == id_buscado:
            nuevo_estado = input(
                "Ingrese el nuevo estado (en progreso/resuelto): ")
            try:
                tecnico.actualizar_estado(t, nuevo_estado)
            except TicketYaResueltoError as error:
                print(f"\n⚠️  {error}\n")
            return

    print(f"\n❌ No se encontró un ticket con el ID #{id_buscado}.\n")
