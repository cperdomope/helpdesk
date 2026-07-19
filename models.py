class TicketYaResueltoError(Exception):
    """Se lanza cuando se intenta modificar un ticket que ya está resuelto."""
    pass


def nuevo_ticket(id: int, usuario: str, asunto: str, categoria: str, prioridad: str) -> dict:
    return {
        "id": id,
        "usuario": usuario,
        "asunto": asunto,
        "categoria": categoria,
        "estado": "abierto",
        "prioridad": prioridad,
    }


class Ticket:
    def __init__(self, id: int, usuario: str, asunto: str, categoria: str, prioridad: str):
        self.id = id
        self.usuario = usuario
        self.asunto = asunto
        self.categoria = categoria
        self.estado = "abierto"
        self.prioridad = prioridad

    def cambiar_estado(self, nuevo_estado: str) -> None:
        if self.estado == "resuelto":
            raise TicketYaResueltoError(
                f"El ticket #{self.id} ya está resuelto y no puede modificarse.")
        self.estado = nuevo_estado
        print(
            f"\n✅ Ticket #{self.id} actualizado a estado '{nuevo_estado}' con éxito.\n")


class Usuario:
    def __init__(self, nombre: str, correo: str):
        self.nombre = nombre
        self.correo = correo

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.nombre})"


class Cliente(Usuario):
    def __init__(self, nombre: str, correo: str):
        super().__init__(nombre, correo)

    def crear_ticket(self, id: int, asunto: str, categoria: str, prioridad: str) -> Ticket:
        ticket = Ticket(id, self.nombre, asunto, categoria, prioridad)
        print(f"\n✅ {self.nombre} creó el ticket #{ticket.id}.\n")
        return ticket


class Tecnico(Usuario):
    def __init__(self, nombre: str, correo: str):
        super().__init__(nombre, correo)

    def actualizar_estado(self, ticket: Ticket, nuevo_estado: str) -> None:
        ticket.cambiar_estado(nuevo_estado)
        print(f"({self.nombre} realizó esta actualización)\n")
