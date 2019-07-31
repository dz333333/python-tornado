from libs.base.web import patterns
from . import api

urlpatterns = patterns(
    (r'^/list$', api.BrandHandler),
    (r'^/detail/(\d+)', api.BrandDetailHandler),
)
