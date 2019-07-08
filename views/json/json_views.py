import tornado.web
class JsonHandle(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):

        

        self.write("json view")