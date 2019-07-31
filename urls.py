from libs.base.web import patterns
from libs.base.web import include
# from libs.base.web import APINotFoundHandler

urlpatterns = patterns(
    # (r"/login", LoginHandle),
    # (r"/brand_list", BrandListHandle),
    # (r"/brand/(\d+)", BrandDetailHandle),
    # (r"/brand_manager", ManagerHandle),
    # (r"/brand_manager/(\d+)", BrandManagerHandle),
    # (r"/wx", WxHandle),
    # (r"/user", UserHandle),
    (r'^/account$', include('views.login.urls')),
    (r'^/user$', include('views.user.urls')),
    (r'^/brand$', include('views.brand.urls')),
    (r'^/manager$', include('views.manager.urls')),
    # (r'.*', APINotFoundHandler)
)
