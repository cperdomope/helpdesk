# HelpDesk — Ruta de Aprendizaje Incremental

> Proyecto: Sistema de Gestion de Tickets e Incidencias
> Dedicacion: 2 horas diarias
> Total estimado: 23 dias (46 horas)

---

## Diagnostico Inicial

| Componente                                 | Estado                                         |
| ------------------------------------------ | ---------------------------------------------- |
| CLI con menu interactivo                   | Completado                                     |
| Modularidad (main/models/actions)          | Completado                                     |
| Type hints y excepciones                   | Completado                                     |
| POO con herencia (Usuario/Tecnico/Cliente) | Completado                                     |
| SQLAlchemy + Modelos ORM                   | Parcial (creado pero no integrado con consola) |
| Flask con web y Tailwind                   | Parcial (funciona pero faltan features)        |
| Base de datos conectada                    | Funcional                                      |
| Pruebas unitarias                          | Pendiente                                      |
| Asincronia / Concurrencia                  | Pendiente                                      |
| Despliegue / DevOps                        | Pendiente                                      |

**Brecha critica:** El codigo de consola (`main.py`, `actions.py`) usa datos en memoria
con las clases viejas. Los modelos SQLAlchemy existen pero no se usan desde consola.

---

## Bloque 1: Cerrar la Base de Datos (Fase 4 real)

> Objetivo: Migrar la consola a usar la BD y entender SQLAlchemy a fondo.

---

### Dia 1 — SQLAlchemy profundo

**Duracion:** 2 horas

**Temas a estudiar:**

- Que es `declarative_base()` y como registra los modelos en `Base.metadata`
- `scoped_session` vs `sessionmaker` — por que usamos `scoped_session` en Flask
- `back_populates` vs `backref` — como se resuelven las relaciones bidireccionales
- `session.query()`, `session.add()`, `session.commit()`, `session.close()`

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                                         |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:30 | Leer `database.py` linea por linea. Inspeccionar `Base.metadata.tables` en consola para ver todas las tablas registradas.                                         |
| 0:30–1:00 | Leer `models.py`. Entender por que `Usuario` hereda de `Base` Y de `UserMixin`. Buscar en la doc de SQLAlchemy que hace cada tipo de `Column`.                    |
| 1:00–1:30 | Comparar `back_populates="creador"` con `backref`. Entender por que `foreign_keys` es necesario cuando un modelo tiene dos relaciones hacia el mismo otro modelo. |
| 1:30–2:00 | Abrir terminal y ejecutar: crear un usuario y un ticket usando `SessionLocal` directamente. Consultar con `db.query(Ticket).all()`.                               |

**Ejercicio practico:**

```python
from database import SessionLocal
from models import Usuario, Ticket

db = SessionLocal()
u = Usuario(username="test", nombre="Test User", email="test@test.com", rol="tecnico")
u.set_password("123456")
db.add(u)
db.commit()
```

**Preguntas para autoevaluacion:**

- Que diferencia hay entre `session.get(Ticket, 1)` y `db.query(Ticket).first()`?
- Que hace `onupdate=` en `fecha_actualizacion`?
- Que pasaria si eliminas `nullable=False` de un campo? Crea la migracion y comprueba.

**Conceptos clave:** `Column`, `ForeignKey`, `relationship`, `session.add()`, `session.commit()`, `session.query()`.

---

### Dia 2 — Migraciones con Alembic

**Duracion:** 2 horas

**Temas a estudiar:**

- Alembic es como "Git pero para la base de datos"
- Cada migracion es un archivo con `upgrade()` y `downgrade()`
- `--autogenerate` compara los modelos con la BD actual

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                                                                                                                          |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:20 | Instalar: `pip install alembic`. Ejecutar `alembic init alembic` en la raiz del proyecto.                                                                                                                                                          |
| 0:20–0:50 | Configurar `alembic.ini`: cambiar la linea `sqlalchemy.url` para que apunte a tu BD MySQL. Editar `env.py` para que importe `Base` de `database.py`.                                                                                               |
| 0:50–1:30 | Crear primera migracion: `alembic revision --autogenerate -m "initial"`. Inspeccionar el archivo generado en `alembic/versions/`. Ejecutar `alembic upgrade head`.                                                                                 |
| 1:30–2:00 | Ejercicio: agregar campo `telefono` a `Usuario`. Crear migracion con `alembic revision --autogenerate -m "add telefono"`. Revisar que `op.add_column()` este en `upgrade()`. Ejecutar `alembic upgrade head`. Luego probar `alembic downgrade -1`. |

**Conceptos clave:** `alembic init`, `--autogenerate`, `upgrade()`, `downgrade()`, `op.add_column()`, `op.drop_column()`, `op.alter_column()`.

**Archivos que crea Alembic:**

```
alembic/
  versions/         # Migraciones (archivos .py)
  env.py            # Configuracion del entorno de migraciones
  script.py.mako    # Plantilla para nuevos revisiones
alembic.ini         # Configuracion principal (URL de BD)
```

---

### Dia 3 — Reparar la consola (unificar con BD)

**Duracion:** 2 horas

**Temas a estudiar:**

- Por que el codigo viejo (`actions.py`) usa listas en RAM
- Como reemplazar esas listas por consultas SQLAlchemy
- Eliminar las clases viejas (`Cliente`, `Tecnico`, `Administrador`) y usar solo los modelos ORM

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                                                                                             |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:30 | Leer `actions.py` y `main.py` linea por linea. Identificar: `tickets = list[Ticket]` (linea 3 de actions.py), las funciones `crear_ticket`, `listar_tickets`, `asignar_ticket`.                                       |
| 0:30–1:30 | Reescribir `actions.py`: reemplazar toda la logica de listas en RAM por consultas SQLAlchemy. Usar `SessionLocal()` en cada funcion. Cada funcion ahora hace `db = SessionLocal()` al inicio y `db.close()` al final. |
| 1:30–2:00 | Reescribir `main.py`: eliminar import de clases viejas. Usar `Usuario` y `Ticket` de SQLAlchemy. Ajustar el menu para autenticar contra la BD.                                                                        |

**Resultado esperado:** `main.py` ya no necesita las clases viejas. Puedes ejecutar `python main.py` y ver los mismos tickets que en la web.

**Archivos a modificar:**

- `actions.py` — toda la logica
- `main.py` — imports y autenticacion

**Archivo a archivar (renombrar):**

- `models.py` viejo (con `Cliente`, `Tecnico`, `Administrador`) -> los modelos ORM ya los reemplazan

---

## Bloque 2: Web — Profundidad (Fase 4 extendida)

> Objetivo: Entender cada pieza de Flask y agregar features empresariales.

---

### Dia 4 — Flask a fondo

**Duracion:** 2 horas

**Temas a estudiar:**

- Ciclo request-response en Flask: cliente envia HTTP -> Flask busca ruta -> ejecuta funcion -> retorna respuesta
- Contexto de aplicacion (`app_context`) vs contexto de request (`request_context`)
- Por que `SessionLocal` es `scoped_session` — una sesion por request HTTP, no una global

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                   |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:40 | Leer la documentacion de Flask sobre "Application Context" y "Request Context". Entender que `g` es un objeto temporal por request.         |
| 0:40–1:10 | Estudiar el patron de fabrica de aplicaciones Flask: `create_app()`. No implementarlo aun, solo entenderlo.                                 |
| 1:10–1:40 | Implementar manejadores de error HTTP: crear `@app.errorhandler(404)` y `@app.errorhandler(403)` que rendericen paginas de error amigables. |
| 1:40–2:00 | Crear ruta `/health` que devuelva JSON confirmando que la BD responde.                                                                      |

**Conceptos clave:** `g`, `current_app`, `request`, `session` (Flask cookie vs SQLAlchemy ORM), `app.teardown_appcontext`.

---

### Dia 5 — Jinja2 + Tailwind

**Duracion:** 2 horas

**Temas a estudiar:**

- Herencia de templates: `{% extends "base.html" %}`
- Bloques: `{% block title %}`, `{% block content %}`
- Filtros Jinja2: `|capitalize`, `|replace`, `|default`, `|length`
- Macros: `{% macro input(name, type) %}`

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                      |
| --------- | ------------------------------------------------------------------------------------------------------------------------------ |
| 0:00–0:30 | Revisar la herencia que ya existe en los templates (`{% extends "base.html" %}`). Entender como `block content` se rellena.    |
| 0:30–1:00 | Crear filtros personalizados en `app.py` con `@app.template_filter()`. Ejemplo: filtro `datetimeformat` para formatear fechas. |
| 1:00–1:30 | Mejorar `base.html`: agregar sidebar de navegacion, indicador de rol con colores, breadcrumbs.                                 |
| 1:30–2:00 | Ejercicio: agregar modo oscuro con Tailwind (clases `dark:`). Usar `localStorage` para persistir la preferencia del usuario.   |

**Conceptos clave:** `{% macro %}`, `{% set %}`, `|safe`, `autoescape`, `@app.template_filter()`.

---

### Dia 6 — Autenticacion real

**Duracion:** 2 horas

**Temas a estudiar:**

- `flask-login`: `LoginManager`, `user_loader`, `login_user()`, `logout_user()`
- `current_user`: proxy que representa al usuario logueado
- Proteccion CSRF: cada formulario POST debe incluir un token
- `werkzeug.security`: `generate_password_hash` y `check_password_hash`

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                                                            |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0:00–0:40 | Leer el codigo de `app.py` desde `login_manager` hasta `load_user`. Entender que hace cada linea.                                                                                    |
| 0:40–1:10 | Instalar `flask-wtf` y agregar proteccion CSRF a todos los formularios HTML. Agregar `{{ form.csrf_token }}` o `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`. |
| 1:10–1:40 | Mejorar login: agregar campo "Recordarme" (usar `remember=True` en `login_user()`), mostrar ultimo acceso en el dashboard.                                                           |
| 1:40–2:00 | Ejercicio: bloquear cuenta tras 5 intentos fallidos. Agregar campo `intentos_fallidos` y `bloqueado_hasta` a `Usuario`.                                                              |

**Conceptos clave:** `login_required`, `current_user`, `is_authenticated`, `is_active`, `session` (cookie firmada), `itsdangerous`.

---

### Dia 7 — Roles y permisos

**Duracion:** 2 horas

**Temas a estudiar:**

- Decoradores en Python: que es un decorador, como funciona `@decorador`
- `functools.wraps`: preservar metadatos de la funcion original
- Decoradores con argumentos: el patron de 3 niveles de funciones anidadas

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                                                |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0:00–0:40 | Crear decorator `rol_requerido(*roles)` en un archivo `utils.py`. Verificar que `current_user.rol` este en la tupla de roles permitidos. Si no, redirigir o abortar 403. |
| 0:40–1:10 | Refactorizar `app.py`: reemplazar todos los `if not current_user.es_admin: flash(...)` por `@rol_requerido("admin")`.                                                    |
| 1:10–1:40 | Crear `@app.before_request` que registre cada acceso a ruta protegida en la tabla `HistorialTicket` o en un archivo de log.                                              |
| 1:40–2:00 | Ejercicio: crear una vista `/admin/solo-admins` accesible solo por admins, y `/tecnico/solo-tecnicos` accesible solo por tecnicos.                                       |

**Concepto clave:** `functools.wraps`, decoradores con argumentos, `before_request`, `abort(403)`.

---

### Dia 8 — Subir archivos adjuntos

**Duracion:** 2 horas

**Temas a estudiar:**

- `werkzeug.datastructures.FileStorage`: como Flask maneja archivos subidos
- `secure_filename()`: sanitizar nombres de archivo
- `MAX_CONTENT_LENGTH`: limite de tamano para subidas

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                   |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:30 | Crear modelo `ArchivoAdjunto` en `models.py`: `id`, `ticket_id` (FK), `nombre_original`, `nombre_guardado`, `tamano_bytes`, `fecha_subida`. |
| 0:30–1:00 | Crear carpeta `static/uploads/` en el proyecto. Crear ruta `/tickets/<id>/adjuntar` que reciba el archivo con `request.files`.              |
| 1:00–1:30 | Guardar el archivo con `secure_filename()`, registrar en BD, registrar en historial.                                                        |
| 1:30–2:00 | Mostrar adjuntos en `ver_ticket.html`: enlaces de descarga con iconos por tipo de archivo (imagen, PDF, otro).                              |

**Conceptos clave:** `request.files`, `secure_filename()`, `MAX_CONTENT_LENGTH`, `os.makedirs()`, tipos MIME.

---

### Dia 9 — Notificaciones por email

**Duracion:** 2 horas

**Temas a estudiar:**

- `smtplib` de Python estandar: enviar correos SMTP
- `email.mime.text.MIMEText`: construir el cuerpo del email
- Mailtrap.io: servicio gratis para probar envio de correos sin enviar emails reales

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                                        |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:30 | Crear cuenta en Mailtrap.io (gratis). Obtener credenciales SMTP. Agregar a `.env`: `MAIL_HOST`, `MAIL_PORT`, `MAIL_USER`, `MAIL_PASS`.                           |
| 0:30–1:15 | Crear funcion `enviar_email(destinativo, asunto, cuerpo)` en `utils.py`. Probar que envia correctamente. Usarla al crear ticket: enviar confirmacion al creador. |
| 1:15–1:45 | Usar la funcion al cambiar estado: notificar al creador y al tecnico asignado.                                                                                   |
| 1:45–2:00 | Ejercicio: crear template de email HTML con Jinja2 (`templates/email/ticket_creado.html`).                                                                       |

**Conceptos clave:** `smtplib.SMTP`, `MIMEText`, `MIMEMultipart`, variables de entorno, templates de email.

---

### Dia 10 — Dashboard con graficas

**Duracion:** 2 horas

**Temas a estudiar:**

- Chart.js: libreria JavaScript para graficas, se incluye via CDN
- Tipos de graficas: `doughnut` (circulos), `bar` (barras), `line` (lineas de tiempo)
- `jsonify` de Flask: convertir Python dicts a respuestas JSON

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                            |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| 0:00–0:30 | Crear endpoint `/api/dashboard/stats` que devuelva JSON con: tickets por estado, tickets por tecnico, tiempo promedio de resolucion. |
| 0:30–1:00 | Agregar Chart.js via CDN en `dashboard.html`. Crear grafica doughnut de tickets por estado.                                          |
| 1:00–1:30 | Crear grafica de barras de tickets por tecnico.                                                                                      |
| 1:30–2:00 | Ejercicio: grafica de lineas con tickets creados por dia (ultimos 7 dias). Usar `func.date_trunc` de SQLAlchemy.                     |

**Conceptos clave:** `jsonify`, `func.count`, `func.date_trunc`, `GROUP BY` con SQLAlchemy, Chart.js.

---

### Dia 11 — Paginacion y busqueda

**Duracion:** 2 horas

**Temas a estudiar:**

- Paginacion: `query.limit(20).offset((page-1)*20)`
- Busqueda por texto: `Ticket.titulo.ilike(f'%{texto}%')`
- Filtros combinados: estado + prioridad + busqueda + pagina

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                 |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:30 | Agregar parametro `?page=1&per_page=20` a la ruta `/tickets`. Calcular offset. Obtener total de registros para saber cuantas paginas hay. |
| 0:30–1:00 | Mostrar controles de paginacion en `tickets.html`: "Anterior", numeros de pagina, "Siguiente".                                            |
| 1:00–1:30 | Agregar campo de busqueda de texto libre que filtre por titulo o descripcion.                                                             |
| 1:30–2:00 | Unificar busqueda + estado + prioridad + pagina en una sola URL. Probar que funciona todo junto.                                          |

**Conceptos clave:** `limit()`, `offset()`, `ilike`, `func.count()`, parametros de query string.

---

## Bloque 3: Pruebas y Control de Calidad (Fase 5)

> Objetivo: Garantizar que el sistema funcione correctamente y aprender testing profesional.

---

### Dia 12 — pytest basico

**Duracion:** 2 horas

**Temas a estudiar:**

- pytest: el estandar de testing en Python
- Convencion: archivos `test_*.py`, funciones `test_*()`
- `assert`: la forma de verificar que algo es correcto
- `pytest.fixture`: configuracion reutilizable para tests

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:30 | Instalar: `pip install pytest`. Crear carpeta `tests/` con `__init__.py` vacio.                                                          |
| 0:30–0:45 | Crear `tests/conftest.py` con fixture que cree una BD SQLite en memoria y devuelva una sesion.                                           |
| 0:45–1:15 | Crear `tests/test_models.py`: test de crear usuario, test de `check_password`, test de crear ticket con relacion a usuario.              |
| 1:15–1:45 | Crear `tests/test_models.py`: test de que un ticket nuevo esta en estado "abierto", test de que `__repr__` devuelve el formato correcto. |
| 1:45–2:00 | Ejecutar `pytest -v` y verificar que todos los tests pasan (marcadores verdes).                                                          |

**Conceptos clave:** `assert`, `pytest.fixture`, `scope`, `conftest.py`, `pytest -v`.

---

### Dia 13 — Tests de integracion con BD de prueba

**Duracion:** 2 horas

**Temas a estudiar:**

- Tests de integracion: probar que multiples componentes funcionan juntos
- SQLite en memoria: `sqlite:///:memory:` — BD rapida que se borra al cerrar
- `app.test_client()`: simular requests HTTP sin levantar el servidor

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                   |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:30 | Configurar Flask para usar SQLite en memoria en modo testing. Crear fixture `test_app`.                                                     |
| 0:30–1:00 | Crear `tests/test_routes.py`: test de que la ruta `/login` retorna 200, test de login correcto, test de login con credenciales incorrectas. |
| 1:00–1:30 | Test de que un usuario no autenticado es redirigido a `/login`. Test de que un usuario puede crear un ticket.                               |
| 1:30–2:00 | Test de autorizacion: crear dos usuarios, que uno intente ver el ticket del otro, verificar que recibe error 403 o redireccion.             |

**Conceptos clave:** `app.config['TESTING']`, `app.test_client()`, `assert response.status_code == 200`, `assert b'Texto' in response.data`.

---

### Dia 14 — TDD (Test-Driven Development)

**Duracion:** 2 horas

**Temas a estudiar:**

- Filosofia TDD: Rojo (fallo) -> Verde (pasa) -> Refactorizar
- Escribir el test ANTES del codigo que lo hace pasar
- `pytest.mark.parametrize`: probar multiples escenarios con un solo test

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                                   |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:30 | Leer sobre TDD en la doc de Python. Entender el ciclo.                                                                                                      |
| 0:30–1:00 | Ejercicio 1: escribir test de que "un tecnico no puede asignarse un ticket que ya tiene otro tecnico". Luego implementar la logica que haga pasar el test.  |
| 1:00–1:30 | Ejercicio 2: test de que "admin puede ver todos los tickets". Implementar endpoint si no existe.                                                            |
| 1:30–2:00 | Refactorizar: aplicar TDD a la funcion `cambiar_estado` — escribir tests para todos los casos (estado invalido, ticket resuelto, etc.) y limpiar el codigo. |

**Conceptos clave:** Ciclo TDD, `pytest.mark.parametrize`, `pytest.raises`, tests de borde (edge cases).

---

### Dia 15 — Concurrencia con asyncio

**Duracion:** 2 horas

**Temas a estudiar:**

- `asyncio`: ejecutar tareas en paralelo sin hilos
- `async/await`: la sintaxis para funciones asincronas
- Race condition: que pasa cuando dos procesos modifican lo mismo al mismo tiempo
- Solucion: `SELECT ... FOR UPDATE` con SQLAlchemy

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                                                    |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:40 | Leer documentacion basica de `asyncio`. Ejecutar `asyncio.sleep()` con `asyncio.gather()`.                                                                                   |
| 0:40–1:10 | Crear script `scripts/simular_tickets.py` que genere 100 tickets automaticos usando `asyncio.gather()`.                                                                      |
| 1:10–1:40 | Demostrar race condition: simular 10 procesos intentando asignar el mismo ticket. Verificar que alguno falla. Solucionar con `Ticket.query.with_for_update()` en SQLAlchemy. |
| 1:40–2:00 | Ejercicio: implementar bloqueo optimista agregando campo `version` a `Ticket`. Incrementar en cada actualizacion y verificar antes de guardar.                               |

**Conceptos clave:** `asyncio.gather`, `asyncio.create_task`, race condition, `with_for_update()`, bloqueo optimista vs pesimista.

---

## Bloque 4: Produccion y DevOps

> Objetivo: Llevar la app a un entorno real.

---

### Dia 16 — Variables de entorno

**Duracion:** 2 horas

**Temas a estudiar:**

- `python-dotenv`: cargar variables de archivo `.env`
- Separar configuracion de codigo: nunca hardcodear secretos
- Clases de configuracion: `Config` base, `DevelopmentConfig`, `ProductionConfig`

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                             |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:30 | Instalar `pip install python-dotenv`. Crear archivo `.env` con `DB_URL`, `SECRET_KEY`, `MAIL_HOST`, `MAIL_PORT`, `MAIL_USER`, `MAIL_PASS`.            |
| 0:30–1:00 | Crear `config.py` con clase `Config` que lea todas las variables. `DevelopmentConfig` usa MySQL local, `ProductionConfig` usa la variable de entorno. |
| 1:00–1:30 | Modificar `database.py` y `app.py` para que usen `config.py` en lugar de valores hardcodeados.                                                        |
| 1:30–2:00 | Crear `.env.example` (sin valores reales) y agregar `.env` a `.gitignore`. Verificar que el proyecto carga bien las variables.                        |

**Conceptos clave:** `os.getenv()`, `load_dotenv()`, `.gitignore`, `FLASK_ENV`, Herencia de clases de configuracion.

---

### Dia 17 — Dockerizar

**Duracion:** 2 horas

**Temas a estudiar:**

- Docker: empaquetar la app en un contenedor
- `Dockerfile`: instrucciones para construir la imagen
- `docker-compose.yml`: definir multiples servicios (app + BD)

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                                                                   |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:30 | Crear `Dockerfile`: `FROM python:3.12-slim`, instalar dependencias de sistema (`default-mysql-client`), copiar `requirements.txt`, instalar paquetes Python, copiar codigo. |
| 0:30–1:00 | Crear `docker-compose.yml` con servicios `web` (la app Flask) y `db` (MySQL 8). Configurar variables de entorno, puertos, volumen para la BD.                               |
| 1:00–1:30 | Ejecutar `docker-compose up --build`. Verificar que la app levanta y se puede loguear con `admin / admin123`.                                                               |
| 1:30–2:00 | Configurar volumenes para que la BD persista datos entre reinicios. Crear `.dockerignore` para excluir `venv/`, `__pycache__/`, `.git/`.                                    |

**Conceptos clave:** `Dockerfile` (FROM, COPY, RUN, CMD), `docker-compose.yml` (services, volumes, ports, depends_on), `.dockerignore`.

---

### Dia 18 — Logging y monitoreo

**Duracion:** 2 horas

**Temas a estudiar:**

- `logging` de Python: el modulo estandar para registros
- Niveles de log: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- `RotatingFileHandler`: archivos de log que no crezcan infinitamente
- Por que `print()` no sirve en produccion

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                     |
| --------- | ----------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:30 | Reemplazar `print()` por `logging.info()` y `logging.error()` en `app.py`. Configurar formato con timestamp, nivel y mensaje. |
| 0:30–1:00 | Crear `RotatingFileHandler` que guarde logs en `logs/app.log` (max 5MB, 3 archivos de backup).                                |
| 1:00–1:30 | Reforzar `/health` para que verifique: conexion a BD (`SELECT 1`), espacio en disco, tiempo de respuesta.                     |
| 1:30–2:00 | Ejercicio: crear comando `flask seed-db` que siembre 10 usuarios y 50 tickets de prueba para tener datos reales de testing.   |

**Conceptos clave:** `logging.getLogger()`, `logging.basicConfig()`, `RotatingFileHandler`, `app.logger`, health checks.

---

### Dia 19 — Despliegue

**Duracion:** 2 horas

**Temas a estudiar:**

- Gunicorn (Linux/Mac) o Waitress (Windows): servidores WSGI para produccion
- `requirements.txt`: listar todas las dependencias
- Procfile: instruccion para plataformas como Render/Railway

**Paso a paso:**

| Tiempo    | Actividad                                                                                                                               |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:40 | Instalar waitress (Windows): `pip install waitress`. Probar: `waitress-serve --port=5000 app:app`. Verificar que la app funciona igual. |
| 0:40–1:00 | Generar `requirements.txt`: `pip freeze > requirements.txt`. Limpiar paquetes innecesarios.                                             |
| 1:00–1:20 | Crear cuenta en Railway.app (gratis). Conectar repo de GitHub. Configurar variables de entorno en el dashboard.                         |
| 1:20–2:00 | Publicar. Verificar que la app corre con HTTPS. Probar login + creacion de ticket desde produccion.                                     |

**Conceptos clave:** `waitress-serve`, `requirements.txt`, `Procfile`, `RAILWAY_*` env vars, HTTPS, despliegue continuo (auto-deploy on push).

---

## Bloque 5: Extras (Opcional)

> Objetivo: Explorar caminos de especializacion. Elige UNO segun tu interes.

---

### Dia 20 — API REST con Flask

**Duracion:** 2 horas

| Tiempo    | Actividad                                                                                                                              |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:40 | Crear blueprint `api` en `api.py`. Rutas: `GET /api/tickets`, `POST /api/tickets`, `GET /api/tickets/<id>`, `PATCH /api/tickets/<id>`. |
| 0:40–1:10 | Instalar `PyJWT`. Crear endpoint `POST /api/login` que devuelva un token JWT. Decorador `@jwt_requerido` para proteger rutas.          |
| 1:10–1:40 | Agregar docstrings con formato OpenAPI a cada ruta.                                                                                    |
| 1:40–2:00 | Probar con curl o Postman: login -> obtener token -> listar tickets.                                                                   |

---

### Dia 21 — WebSockets (tiempo real)

**Duracion:** 2 horas

| Tiempo    | Actividad                                                                                                            |
| --------- | -------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:40 | Instalar `flask-socketio`. Configurar SocketIO en `app.py`. Probar eventos basicos `connect`, `disconnect`.          |
| 0:40–1:20 | Cuando un ticket cambia de estado, emitir evento `ticket_actualizado` a todos los tecnicos conectados via WebSocket. |
| 1:20–2:00 | Agregar badge en navbar con contador de tickets no leidos que se actualice en tiempo real.                           |

---

### Dia 22 — Refactor a FastAPI (opcional avanzado)

**Duracion:** 2 horas

| Tiempo    | Actividad                                                                                                                          |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:40 | Crear `main_api.py` con FastAPI. Reutilizar los modelos SQLAlchemy existentes.                                                     |
| 0:40–1:20 | Migrar rutas de Flask a FastAPI: Path Operations en vez de `@app.route()`, Dependency Injection en vez de `SessionLocal()` manual. |
| 1:20–2:00 | Probar la documentacion automatica de Swagger en `/docs`. Comparar la experiencia con Flask.                                       |

---

### Dia 23 — Frontend con React (opcional avanzado)

**Duracion:** 2 horas

| Tiempo    | Actividad                                                                                            |
| --------- | ---------------------------------------------------------------------------------------------------- |
| 0:00–0:40 | Crear proyecto con Vite: `npm create vite@latest helpdesk-ui -- --template react`. Instalar `axios`. |
| 0:40–1:20 | Crear componentes Login y Dashboard. Conectar con la API Flask en `http://localhost:5000/api/`.      |
| 1:20–2:00 | Almacenar JWT en `localStorage`. Enviar token en headers de cada request.                            |

---

## Resumen de Tecnologias a Aprender

| Tecnologia                | Bloque   | Dias  |
| ------------------------- | -------- | ----- |
| SQLAlchemy ORM            | Bloque 1 | 1–3   |
| Alembic                   | Bloque 1 | 2     |
| Flask                     | Bloque 2 | 4–11  |
| Jinja2                    | Bloque 2 | 5     |
| Tailwind CSS              | Bloque 2 | 5     |
| Flask-Login               | Bloque 2 | 6     |
| Werkzeug (files, hashing) | Bloque 2 | 6, 8  |
| Chart.js                  | Bloque 2 | 10    |
| pytest                    | Bloque 3 | 12–14 |
| asyncio                   | Bloque 3 | 15    |
| python-dotenv             | Bloque 4 | 16    |
| Docker / docker-compose   | Bloque 4 | 17    |
| logging                   | Bloque 4 | 18    |
| waitress / gunicorn       | Bloque 4 | 19    |
| flask-socketio            | Bloque 5 | 21    |
| FastAPI                   | Bloque 5 | 22    |
| React                     | Bloque 5 | 23    |

---

## Progreso Diario (checklist)

- [ ] Dia 1 — SQLAlchemy profundo
- [ ] Dia 2 — Migraciones con Alembic
- [ ] Dia 3 — Reparar la consola (unificar con BD)
- [ ] Dia 4 — Flask a fondo
- [ ] Dia 5 — Jinja2 + Tailwind
- [ ] Dia 6 — Autenticacion real
- [ ] Dia 7 — Roles y permisos
- [ ] Dia 8 — Subir archivos adjuntos
- [ ] Dia 9 — Notificaciones por email
- [ ] Dia 10 — Dashboard con graficas
- [ ] Dia 11 — Paginacion y busqueda
- [ ] Dia 12 — pytest basico
- [ ] Dia 13 — Tests de integracion
- [ ] Dia 14 — TDD
- [ ] Dia 15 — Concurrencia (asyncio)
- [ ] Dia 16 — Variables de entorno
- [ ] Dia 17 — Dockerizar
- [ ] Dia 18 — Logging y monitoreo
- [ ] Dia 19 — Despliegue
- [ ] Dia 20 — API REST (extra)
- [ ] Dia 21 — WebSockets (extra)
- [ ] Dia 22 — FastAPI (extra)
- [ ] Dia 23 — React (extra)

---

## Recomendacion Final

Orden sugerido: Dias 1 a 19 en secuencia. Los extras (20–23) son caminos de especializacion: elige UNO segun tu interes.

Cada dia esta diseñado para que al terminar tengas algo concreto funcionando. Si un dia se te complica, reduce el alcance pero no lo saltes: cada concepto se apoya en el anterior.
