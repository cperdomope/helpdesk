from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

URL_BASE_DATOS = "mysql+pymysql://root:root@localhost/helpdesk_db"

engine = create_engine(URL_BASE_DATOS, echo=False)

SessionFactory = sessionmaker(bind=engine)
SessionLocal = scoped_session(SessionFactory)

Base = declarative_base()


def init_db():
    from models import Usuario, Ticket, HistorialTicket, Comentario
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
