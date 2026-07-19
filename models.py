def nuevo_ticket(id: int, usuario: str, asunto: str, categoria: str, prioridad: str) -> dict:
    return {
        "id": id,
        "usuario": usuario,
        "asunto": asunto,
        "categoria": categoria,
        "estado": "abierto",
        "prioridad": prioridad,
    }
