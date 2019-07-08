import tornado
import os
from views.web.web_views import WebHandle
from views.json.json_views import JsonHandle
from views.login.login import LoginHandle
from views.brand.brand import BrandListHandle
from views.brand.brand import BrandDetailHandle
from views.brand.brand import BrandManagerHandle
from views.brand.brand import ManagerHandle
from views.wx.wx import WxHandle
from views.user.user import UserHandle


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/web", WebHandle),
            (r"/json", JsonHandle),
            (r"/login", LoginHandle),
            (r"/brand_list", BrandListHandle),
            (r"/brand/(\d+)", BrandDetailHandle),
            (r"/brand_manager", ManagerHandle),
            (r"/brand_manager/(\d+)", BrandManagerHandle),
            (r"/wx", WxHandle),
            (r"/user", UserHandle),
        ]
        setting = dict(
            debug=True,
            autoreload=True,
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            template_path=os.path.join(os.path.dirname(__file__), 'templates')
        )
        tornado.web.Application.__init__(self, handlers, **setting)


if __name__ == "__main__":
    print('Tornado server is ready for service\r')
    Application().listen(8000, xheaders=True)
    tornado.ioloop.IOLoop.current().start()
