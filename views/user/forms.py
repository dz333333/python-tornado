from wtforms_tornado import Form
from wtforms.fields import StringField
from wtforms.fields import IntegerField
from wtforms.validators import DataRequired as DR


class UserForm(Form):
    page = IntegerField(validators=[DR()])
    limit = IntegerField(validators=[DR()])
    name = StringField()
    phone = StringField()


class AddUserForm(Form):
    name = StringField(validators=[DR()])
    phone = StringField(validators=[DR()])


class UpdateUserForm(Form):
    id = IntegerField(validators=[DR()])
    name = StringField(validators=[DR()])
    phone = StringField(validators=[DR()])


class DeleteUserForm(Form):
    id = IntegerField(validators=[DR()])

