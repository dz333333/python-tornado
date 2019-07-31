import re
import json
import hashlib
import traceback
from importlib import import_module

from tornado import gen
from tornado.log import gen_log
from tornado.web import HTTPError
from tornado.web import RequestHandler
from tornado.options import options

from libs.base.db import DBObject
from libs.tools.widget import Common
# from libs.base.redis import RedisObject
from libs.tools.parse_helper import Parse
from libs.tools.jwt_helper import JwtHelper
from libs.enums.response_status import ResStatus


def include(arg):
    urlconf_module = import_module(arg)
    url_list = getattr(urlconf_module, 'urlpatterns', urlconf_module)
    return url_list


def patterns(*args):
    pattern_list = []
    for t in args:
        if not isinstance(t, (list, tuple)):
            continue
        url, handlers = t
        if isinstance(handlers, type):
            pattern_list.append((url, handlers))
        elif isinstance(handlers, (list, tuple)):
            for url_postfix, h in handlers:
                new_url = (url + url_postfix).replace("$^", "")
                pattern_list.append((new_url, h))
    return pattern_list


class BaseHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.body_dict = {}
        self.response_info = {'status': 0, 'message': 'success', 'data': {}}
        self.db_conns = {}
        self.db = None  # 默认数据库
        self.redis = None  # 默认Redis
        self.redis_conns = {}
        self.form_data = {}  # 保存wtforms解析后的data
        self.need_cache_request = False  # 是否需要缓存当前请求结果, 默认False
        self.time_of_cache_request = None  # 单位秒, 缓存时间, 如果为None将使用默认缓存时间
        self.server_error = None  # 服务器error, 自动发送error邮件
        self.auth_token = None  # 解码后的Authorization信息
        self.logger = gen_log  # debug|info|warning|error
        self.set_header('Content-Type', 'application/json')
        self._parse_data_from_body()
        self.access_control_allow()

    def initialize(self):
        pass

    def conn_db(self, db_key):
        db = DBObject(db_key)
        setattr(self, db_key, db)
        self.db_conns[db_key] = db

    # def conn_redis(self, redis_key):
    #     rd = RedisObject(redis_key)
    #     setattr(self, redis_key, rd)
    #     self.redis_conns[redis_key] = rd

    async def prepare(self):
        self.conn_db("db")
        # self.conn_redis("redis")
        # if not hasattr(self, "_current_user"):
        #     self._current_user = await self.get_current_user()

    @gen.coroutine
    def on_finish(self):
        if self.server_error:
            yield self.send_error_email()
        for name in self.db_conns:
            db = self.db_conns[name]
            if db.execute_status is True:
                yield db.rollback()
            yield db.close()

    def write_error(self, status_code, **kwargs):
        """Override"""
        if "exc_info" in kwargs:
            lines = traceback.format_exception(*kwargs["exc_info"])
            self.server_error = lines
            if self.settings.get("serve_traceback"):
                self.set_header('Content-Type', 'text/plain')
                for line in lines:
                    self.write(line)
                self.finish()
            else:
                self.finish("<html><title>%(code)d: %(message)s</title>"
                            "<body>%(code)d: %(message)s</body></html>" % {
                                "code": status_code,
                                "message": self._reason,
                            })

    async def send_error_email(self):
        """
        服务器error, 自动发送error邮件
        """
        receptions = ",".join(options.config["admin_email"])
        if not receptions:
            return
        prefix = options.config.get("email_subject_prefix", "")
        subject = '%s[ERROR] Internal Server Error: %s' % (
            prefix, self.request.path)
        self.server_error.insert(0, subject.replace("[ERROR]", "[ERROR]\n"))
        email = {
            "subject": subject,
            "receptions": receptions,
            "mail_body": self._package_error_mail_body(),
            "mail_body_type": 1
        }
        msg_id = await self.db.insert("common_service.message_email", email)
        main = {
            "msg_type": 1,
            "msg_id": msg_id,
            "priority": 3,
            "appoint_time": Common.current_time()
        }
        await self.db.insert("common_service.message_main", main)
        await self.db.commit()

    def _package_error_mail_body(self):
        """
        拼装error邮件正文, 加入user信息, Request信息
        """
        # request info
        if self.request:
            req_info = {}
            request_key = [
                "_finish_time", "_start_time", "arguments", "body",
                "body_arguments", "files", "host", "host_name", "method",
                "path", "protocol", "query", "query_arguments", "remote_ip",
                "uri", "version"
            ]
            for k in request_key:
                req_info[k] = getattr(self.request, k, "")
            headers_key = [
                "Accept", "Accept-Encoding", "Connection", "Content-Type",
                "User-Agent"
            ]
            for k in headers_key:
                req_info[k] = self.request.headers.get(k, "")
            req_info = Common.utf8(req_info)
            info = json.dumps(req_info, indent=4)
            self.server_error += ["\n", "Request Info:\n", info]
        body = "".join(self.server_error)
        body = body.replace("\n", "<br>").replace(" ", "&nbsp;")
        return body

    def access_control_allow(self):
        # 允许 JS 跨域调用
        access = options.config["remote_access"]
        env = options.config["env"]
        if not access and env not in ["DEV", "TEST"]:
            return
        headers = [
            'Accept, Authorization, DNT, X-CustomHeader, Keep-Alive, ',
            'User-Agent, X-Requested-With, If-Modified-Since, ',
            'Cache-Control, Content-Type'
        ]
        self.set_header(
            "Access-Control-Allow-Methods",
            "GET,PUT,POST,DELETE,OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "".join(headers))
        self.set_header('Access-Control-Allow-Origin', '*')

    def options(self, *args, **kwargs):
        access = options.config["remote_access"]
        env = options.config["env"]
        if not access and env not in ["DEV", "TEST"]:
            self.finish()
        self.set_status(204)
        self.finish()

    def query_arguments(self):
        query_dict = {}
        source = self.request.query_arguments
        for k in source:
            v = Common.utf8(source[k])
            if isinstance(v, (list, tuple)):
                query_dict[k] = (v if len(v) > 1 else v[0])
        return query_dict

    def _request_summary(self):
        """override"""
        return "[%s] [%s] [%s] [%s]" % (
            self.request.method, self.request.version,
            self.request.uri, self.request.remote_ip
        )

    def write_json(self, response, check_token=True):
        """
        1. 将response中的数据格式化, 保证可以安全转为json格式
        2. 将response中包含None的替换为 ""
        :arg response -> eg. {'status': 0, 'message': 'success', 'data': data}
        :arg check_token -> 是否需要检验token是否即将过期
        """
        res = Parse.convert_safe(response)
        res = Parse.remove_none(res)
        res_json = json.dumps(res)
        if response["status"] == 0:
            self.request_cache_save(res_json)
        self.write(res_json)

    def finish_json(self, response):
        """
        :arg response -> eg. {'status': 0, 'message': 'success', 'data': data}
        """
        self.write_json(response)
        self.finish()

    def finish_auto(self, **kwargs):
        '''
        将自动返回self.response_info的信息内容
        确保self.response_info信息正确
        '''
        if kwargs:
            self.set_res_info(**kwargs)
        self.write_json(self.response_info)
        self.finish()

    def set_res_info(self, status, message=None, data=None):
        if status in ResStatus:
            message = message if message else ResStatus[status]
            res_info = {'status': status, 'message': message}
            if data is not None:
                res_info['data'] = data
            self.response_info = res_info
        else:
            raise HTTPError(500)

    def _parse_data_from_body(self):
        """
        1.Content-type = 'application/json;charset=utf-8'
            将http请求发送的json数据解析出来, 保存到 self.body_dict
        2.Content-type = 'multipart/form-data;'
            将http请求发送的数据解析出来, 保存到 self.body_dict
        """
        ctype = self.request.headers.get("Content-type") or ""
        try:
            if 'json' in ctype and self.request.body:
                self.body_dict = json.loads(self.request.body)
            elif 'form-data' in ctype and self.request.body_arguments:
                body_args = self.request.body_arguments
                data = {k: (v[0] if len(v) == 1 else v)
                        for k, v in body_args.items()}
                if self.request.files:
                    data["file"] = self.request.files.get("file")[0]
                self.body_dict = data
        except BaseException:
            pass

    @property
    def user(self):
        return self._current_user

    @user.setter
    def user(self, value):
        self._current_user = value

    async def get_current_user(self):
        '''
        使用 self.user 获取用户信息字典
        :info -> {"user_id": 123, ...}
        '''
        token = self.request.headers.get("Authorization")
        info = JwtHelper().check_token(token)
        if not info or "user_id" not in info:
            return None
        self.auth_token = info
        wheres = {"user_id": info["user_id"], "data_status": 1}
        await self.db.select("auth_user", "*", wheres)
        user_data = self.db.fetchone()
        if not user_data:
            return None
        sql = '''
            SELECT P.perms_code
            FROM auth_user_role UR
            LEFT JOIN auth_role_permission RP ON RP.role_id=UR.role_id AND RP.data_status=1
            LEFT JOIN auth_permission P ON P.perms_id=RP.perms_id AND P.data_status=1
            WHERE UR.user_id=%s AND UR.data_status=1
            GROUP BY perms_code
        '''
        await self.db.execute(sql, (info["user_id"], ))
        perm_data = self.db.fetchall()
        user_data["permissions"] = [x["perms_code"] for x in perm_data]
        return user_data

    def request_cache_save(self, res):
        pass

    def _get_request_cache_uri_hash(self):
        pattern = re.compile(r't=\d*')
        uri = re.sub(pattern, '', self.request.uri)
        uri = uri[:-1] if uri.endswith("&") else uri
        uri_hash = hashlib.md5(uri.encode(encoding='utf-8')).hexdigest()
        return {"uri_hash": uri_hash}


class APINotFoundHandler(BaseHandler):

    def res_of_not_found(self):
        self.set_res_info(4004)
        self.finish_auto()

    def get(self, *args, **kwargs):
        self.res_of_not_found()

    def head(self, *args, **kwargs):
        self.res_of_not_found()

    def post(self, *args, **kwargs):
        self.res_of_not_found()

    def delete(self, *args, **kwargs):
        self.res_of_not_found()

    def patch(self, *args, **kwargs):
        self.res_of_not_found()

    def put(self, *args, **kwargs):
        self.res_of_not_found()
