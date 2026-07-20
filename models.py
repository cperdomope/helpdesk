from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base


class Usuario(Base, UserMixin):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    nombre = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    rol = Column(SAEnum("admin", "tecnico", "usuario", name="rol_enum"), nullable=False, default="usuario")
    activo = Column(Integer, default=1)

    tickets_creados = relationship("Ticket", back_populates="creador", foreign_keys="Ticket.creador_id")
    tickets_asignados = relationship("Ticket", back_populates="tecnico", foreign_keys="Ticket.tecnico_id")
    comentarios = relationship("Comentario", back_populates="autor")
    historiales = relationship("HistorialTicket", back_populates="usuario")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def es_admin(self):
        return self.rol == "admin"

    @property
    def es_tecnico(self):
        return self.rol == "tecnico"

    @property
    def es_usuario(self):
        return self.rol == "usuario"

    def __repr__(self):
        return f"<Usuario {self.username} ({self.rol})>"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    categoria = Column(String(50), nullable=False)
    prioridad = Column(SAEnum("alta", "media", "baja", name="prioridad_enum"), nullable=False, default="media")
    estado = Column(SAEnum("abierto", "en_progreso", "resuelto", "cerrado", name="estado_enum"), nullable=False, default="abierto")
    creador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tecnico_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_actualizacion = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    creador = relationship("Usuario", back_populates="tickets_creados", foreign_keys=[creador_id])
    tecnico = relationship("Usuario", back_populates="tickets_asignados", foreign_keys=[tecnico_id])
    comentarios = relationship("Comentario", back_populates="ticket", order_by="Comentario.fecha.asc()")
    historiales = relationship("HistorialTicket", back_populates="ticket", order_by="HistorialTicket.fecha.asc()")

    def __repr__(self):
        return f"<Ticket #{self.id} - {self.titulo}>"


class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contenido = Column(Text, nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ticket = relationship("Ticket", back_populates="comentarios")
    autor = relationship("Usuario", back_populates="comentarios")

    def __repr__(self):
        return f"<Comentario #{self.id} por {self.autor.username}>"


class HistorialTicket(Base):
    __tablename__ = "historial_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    accion = Column(String(100), nullable=False)
    detalle = Column(Text, nullable=True)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ticket = relationship("Ticket", back_populates="historiales")
    usuario = relationship("Usuario", back_populates="historiales")

    def __repr__(self):
        return f"<HistorialTicket #{self.id} - {self.accion}>"
