from libs.base.decorators import check_form
from libs.base.web import BaseHandler
from . import forms
from . import models


class BrandHandler(BaseHandler):

    @check_form(forms.BrandForm)
    async def get(self):
        model = models.BrandModel(self)
        res = await model.fetch_list(self.form_data)
        self.finish_auto(**res)

    @check_form(forms.AddBrandForm)
    async def post(self):
        model = models.BrandModel(self)
        res = await model.insert_info(self.form_data)
        self.finish_auto(**res)

    @check_form(forms.DeleteBrandForm)
    async def delete(self):
        model = models.BrandModel(self)
        res = await model.delete_info(self.form_data)
        self.finish_auto(**res)


class BrandDetailHandler(BaseHandler):
    async def get(self, id):
        model = models.BrandDetailModel(self, id)
        res = await model.fetch_info()
        self.finish_auto(**res)

    @check_form(forms.UpdateBrandForm)
    async def put(self, id):
        model = models.BrandDetailModel(self, id)
        res = await model.update_info(self.form_data)
        self.finish_auto(**res)
