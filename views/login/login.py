import tornado.web
import pymysql
from base.base_request.base_handler import BaseHandler


class LoginHandle(BaseHandler):
    def post(self):
        db = pymysql.connect("localhost", "root", "password", "test")
        cursor = db.cursor()
        body_data = tornado.escape.json_decode(self.request.body)
        if not body_data.get('name', '') and not body_data.get('password', ''):
            json_res = {
                "status": 400,
                "message": "请填写用户名和密码"
            }
            self.write(json_res)
        elif not body_data.get('name', ''):
            json_res = {
                "status": 400,
                "message": "请填写用户名"
            }
            self.write(json_res)
        elif not body_data.get('password', ''):
            json_res = {
                "status": 400,
                "message": '请填写验证码'
            }
            self.write(json_res)
        else:
            name = body_data['name']
            sql = f"SELECT password FROM USER WHERE NAME ='{name}'"
            print(sql, 'sql')
            cursor.execute(sql)
            data = cursor.fetchone()
            print(type(data) is object)
            if not data:
                json_res = {
                    "status": 400,
                    "message": '用户名不存在'
                }
                self.write(json_res)
            elif data[0] == body_data.get('password'):
                print('success')
                json_res = {
                    "status": 200,
                }
                self.write(json_res)
            else:
                json_res = {
                    "status": 400,
                    "message": '请填写正确的用户名和密码'
                }
                self.write(json_res)

        self.finish()
