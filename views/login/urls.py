from libs.base.web import patterns
from . import api

urlpatterns = patterns(
    (r'^/login$', api.LoginHandler),
)
