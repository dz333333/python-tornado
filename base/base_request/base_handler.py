
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def options(self):
        # 返回方法1
        # self.set_status(204)
        self.finish()
        # 返回方法2
        # self.write('{"errorCode":"00","errorMessage","success"}')

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Methods', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
