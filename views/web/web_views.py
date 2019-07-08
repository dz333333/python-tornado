from base.base_request.base_handler import BaseHandler


class WebHandle(BaseHandler):
    def get(self, *args, **kwargs):
        self.finish()
