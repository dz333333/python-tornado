from wtforms_tornado import Form
from wtforms.fields import StringField
from wtforms.fields import IntegerField
from wtforms.validators import DataRequired as DR


class AddBrandManagerForm(Form):
    manager_id = IntegerField(validators=[DR()])

