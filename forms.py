from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length


class TicketForm(FlaskForm):
    titulo = StringField(
        "Titulo",
        validators=[
            DataRequired(message="El titulo es obligatorio."),
            Length(min=5, max=100,
                   message="El titulo debe tener entre 5 y 100 caracteres.")
        ]
    )
    descripcion = TextAreaField(
        "Descripcion",
        validators=[
            DataRequired(message="La descripcion es obligatoria."),
            Length(min=10, max=200,
                   message="La descripcion debe tener entre 10 y 200 caracteres.")
        ]
    )
    categoria = SelectField(
        "Categoria",
        choices=[("hardware", "Hardware"), ("software", "Software"),
                 ("red", "Red"), ("correo", "Correo"), ("otro", "Otro")],
        validators=[DataRequired()]
    )
    prioridad = SelectField(
        "Prioridad",
        choices=[("alta", "Alta"), ("media", "Media"), ("baja", "Baja")],
        validators=[DataRequired()]
    )
