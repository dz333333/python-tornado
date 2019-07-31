from wtforms_tornado import Form
from wtforms.fields import StringField
from wtforms.validators import DataRequired as DR


class LoginForm(Form):
    name = StringField(validators=[DR()])
    password = StringField(validators=[DR()])
