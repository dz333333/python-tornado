from libs.base.decorators import check_form
from libs.base.web import BaseHandler
from . import forms
from . import models


class UserHandler(BaseHandler):

    @check_form(forms.UserForm)
    async def get(self):
        model = models.UserModel(self)
        res = await model.fetch_list(self.form_data)
        self.finish_auto(**res)

    @check_form(forms.AddUserForm)
    async def post(self):
        model = models.UserModel(self)
        res = await model.insert_info(self.form_data)
        self.finish_auto(**res)

    @check_form(forms.UpdateUserForm)
    async def put(self):
        model = models.UserModel(self)
        res = await model.update_info(self.form_data)
        self.finish_auto(**res)

    @check_form(forms.DeleteUserForm)
    async def delete(self):
        model = models.UserModel(self)
        res = await model.delete_info(self.form_data)
        self.finish_auto(**res)
