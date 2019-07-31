from libs.base.decorators import check_form
from libs.base.web import BaseHandler
from . import forms
from . import models


class BrandManagerHandler(BaseHandler):
    async def get(self, id):
        model = models.BrandManagerModal(self, id)
        res = await model.fetch_info()
        self.finish_auto(**res)

    @check_form(forms.AddBrandManagerForm)
    async def post(self, brand_id):
        model = models.BrandManagerModal(self, brand_id=brand_id)
        res = await model.insert_info(self.form_data)
        self.finish_auto(**res)

    async def delete(self, brand_manager_id):
        model = models.BrandManagerModal(self, brand_manager_id=brand_manager_id)
        res = await model.delete_info()
        self.finish_auto(**res)
