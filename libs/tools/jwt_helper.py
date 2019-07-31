'''
auth采用JWT
'''

import jwt
import time
import datetime

from tornado.options import options


class JwtHelper(object):

    def __init__(self):
        self.secret = options.config["jwt_secret"]
        self.web_jwt_exp = options.config["web_jwt_exp"]

    def _make_token(self, info, exp, source):
        exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=exp)
        info["exp"] = exp  # jwt的过期时间[过期时间必须要大于签发时间]
        info["iat"] = datetime.datetime.now()  # jwt的签发时间
        info["sub"] = source  # jwt所面向的用户
        token = jwt.encode(info, self.secret, algorithm='HS256')
        return str(token, encoding='utf-8')

    def make_web_token(self, user_id):
        info = {"user_id": user_id}
        token = self._make_token(info, self.web_jwt_exp, "web_jwt_exp")
        return token

    def check_token(self, token):
        try:
            token = token[7:] if token and isinstance(token, str) else ""
            token = bytes(token, encoding='utf-8')
            info = jwt.decode(token, self.secret, algorithms=['HS256'])
        except BaseException:
            info = {}
        return info

    def check_token_iat(self, info):
        '''
        有效期不足一小时, 返回False
        小程序的token不使用此检测逻辑
        '''
        if not info or info.get("sub") not in ["miniprogress"]:
            return True
        exp = info.get("exp")
        if exp and (time.time() > (exp - 3600)):
            return False
        return True
