from libs.base.decorators import check_form
from libs.base.web import BaseHandler
from . import forms
from . import models


class LoginHandler(BaseHandler):

    @check_form(forms.LoginForm)
    async def post(self):
        model = models.LoginModel(self)
        res = await model.start(self.form_data)
        self.finish_auto(**res)
