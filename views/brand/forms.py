from wtforms_tornado import Form
from wtforms.fields import StringField
from wtforms.fields import IntegerField
from wtforms.validators import DataRequired as DR


class BrandForm(Form):
    page = IntegerField(validators=[DR()])
    limit = IntegerField(validators=[DR()])
    brand_name = StringField()


class AddBrandForm(Form):
    brand_name = StringField(validators=[DR()])
    brand_category = StringField(validators=[DR()])
    img = StringField(validators=[DR()])


class UpdateUserForm(Form):
    id = IntegerField(validators=[DR()])
    name = StringField(validators=[DR()])
    phone = StringField(validators=[DR()])


class DeleteBrandForm(Form):
    id = IntegerField(validators=[DR()])


class UpdateBrandForm(Form):
    brand_name = StringField(validators=[DR()])
    brand_category = StringField(validators=[DR()])
    img = StringField(validators=[DR()])
    city = StringField(validators=[DR()])
    address = StringField(validators=[DR()])
