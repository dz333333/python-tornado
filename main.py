import os

import tornado.web
import tornado.ioloop
import tornado.httpserver
import wtforms_json

from urls import urlpatterns
from tornado.log import access_log
from tornado.options import define
from tornado.options import options
from tornado.options import parse_command_line
from tornado.options import parse_config_file

define('port', default=None, help='Run on the given port', type=int)
define('settings', default='dev', help='settings file [dev/test/pro]', type=str)
define('mode', default=None, help='setting open mode [message]', type=str)
define('config', default=None, help='config file', type=dict)


class Application(tornado.web.Application):

    def __init__(self):
        settings = {
            'static_path': os.path.join(os.path.dirname(__file__), r"apidoc/doc"),
            'debug': True,
            'gzip': True,
            'xsrf_cookies': False
        }
        super(Application, self).__init__(urlpatterns, **settings)


def main():
    # options.logging = "debug"
    wtforms_json.init()
    parse_command_line(final=False)
    path = os.path.join(os.path.dirname(__file__), 'settings.py')
    parse_config_file(path)
    io_loop = tornado.ioloop.IOLoop.current()
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(options.port)
    access_log.info('Server is running at http://%s:%s' % (options.config["host"], options.port))
    access_log.info('Debug mode has been %s!' % ('OPEN' if options.config["debug"] else 'CLOSE'))
    print('Quit the server with Ctrl+C')
    io_loop.start()


if __name__ == "__main__":
    main()
