"""
框架的函数修饰符
"""
import functools

from tornado.options import options


def check_login(permissions=[]):
    """
    检测用户是否登录
    :permissions -> list, 待校验的权限列表, 用户拥有任一权限即可访问此接口
        e.g. permissions = ["delete_store", "update_store"]
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.user:
                self.set_res_info(4001)
                self.write_json(self.response_info)
                return
            if permissions and not [x for x in permissions if x in self.user["permissions"]]:
                self.set_res_info(4002)
                self.write_json(self.response_info)
                return
            return method(self, *args, **kwargs)
        return wrapper
    return decorator


def check_form(form):
    """
    表单校验
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            form_data = self.query_arguments() if self.request.method == "GET" else self.body_dict
            f = form.from_json(form_data)
            if not f.validate():
                self.set_res_info(4011, data=f.errors)
                self.write_json(self.response_info)
                return
            else:
                self.form_data = f.data
            return method(self, *args, **kwargs)
        return wrapper
    return decorator


def cache_request(cache_time=None):
    """
    根据uri进行缓存, 相同的uri返回的数据一样
    检测是否有缓存, 如果有缓存, 直接返回缓存信息
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if options.config["open_cache"]:
                self.need_cache_request = True
                self.time_of_cache_request = cache_time
                key_format = self._get_request_cache_uri_hash()
                res_json = self.redis.get("request_cache", key_format)
                if res_json:
                    self.write(res_json)
                    self.finish()
                    return
            return method(self, *args, **kwargs)
        return wrapper
    return decorator
