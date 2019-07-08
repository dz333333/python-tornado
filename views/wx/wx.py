from .WXBizDataCrypt import WXBizDataCrypt
from base.base_request.base_handler import BaseHandler
import tornado.web


class WxHandle(BaseHandler):
    def post(self):
        body_data = tornado.escape.json_decode(self.request.body)
        key = body_data.get('key', '')
        data = body_data.get('data', '')
        params_iv = body_data.get('iv', '')
        print(key, 'ddd')
        appId = 'wx93f19fa26be7cb64'
        sessionKey = key
        encryptedData = data
        iv = params_iv

        pc = WXBizDataCrypt(appId, sessionKey)

        print(pc.decrypt(encryptedData, iv))
        self.write(pc.decrypt(encryptedData, iv))
