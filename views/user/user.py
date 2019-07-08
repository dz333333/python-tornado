import pymysql
from base.base_request.base_handler import BaseHandler
import json
from base.date_encoder import DateEncoder
import tornado


class UserHandle(BaseHandler):
    def get(self):
        db = pymysql.connect("localhost", "root", "password",
                             "test", cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        page = self.get_argument("page", '0')
        limit = self.get_argument("limit", '10')
        name = self.get_argument('name', '')
        phone = self.get_argument('phone', '')
        sql = f"SELECT * FROM USER WHERE NAME LIKE '%{name}%' \
           AND PHONE LIKE '%{phone}%' AND NOT VALID = 0  Limit {int(limit)}\
                OFFSET {int(page)*int(limit)}"
        print(sql, 'sql')
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.execute("SELECT count(*) as total FROM USER WHERE NOT \
            VALID =0")
        total = cursor.fetchone().get('total', '')

        # print(isinstance(data,tuple))

        data_list = []
        for item in data:
            # item-->dict
            # item.values-->datetime
            # print(json.dumps(item, cls=DateEncoder), 'fff')
            aa = json.dumps(item, cls=DateEncoder)
            # for k, obj in item.items():
            #     if isinstance(obj, datetime.datetime):
            #         obj = obj.strftime('%Y-%m-%d %H:%M:%S')
            #         item[k] = obj
            data_list.append(json.loads(aa))
        print(data_list)
        data = {
            "data": data_list,
            "total": total
        }
        print(data, ' data')
        # import pdb;pdb.set_trace()
        self.write(json.dumps(data))
        self.finish()

    def post(self):
        db = pymysql.connect("localhost", "root", "password", "test")
        cursor = db.cursor()
        body_data = tornado.escape.json_decode(self.request.body)
        name = body_data.get("name", "")
        phone = body_data.get("phone", "")
        if name and phone:
            sql = f"INSERT INTO USER(NAME, PHONE) VALUES('{name}',\
                '{phone}')"
            try:
                print(sql, 'sql')
                cursor.execute(sql)
                db.commit()
                self.write(
                    json.dumps({
                        "status": 200
                    })
                )
            except Exception:
                db.rollback()
                print('error')
                # 关闭数据库连接
            db.close()
        else:
            self.write(
                json.dumps({
                    "status": 400,
                    "message": "请填写姓名和手机号"
                })
            )

    def delete(self):
        db = pymysql.connect("localhost", "root", "password", "test")
        cursor = db.cursor()
        body_data = tornado.escape.json_decode(self.request.body)
        id = body_data.get("id", None)
        sql = "UPDATE USER SET VALID=0 WHERE ID = %s"
        try:
            cursor.execute(sql, (id, ))
            db.commit()
            self.write(
                json.dumps({
                    "status": 200,
                    "message": '删除成功'
                })
            )
        except Exception:
            db.rollback()
            self.write(
                json.dumps({
                    "status": 400,
                    "message": '删除错误'
                })
            )
        self.finish()
        db.close()

    def put(self):
        db = pymysql.connect("localhost", "root", "password", "test")
        cursor = db.cursor()
        body_data = tornado.escape.json_decode(self.request.body)
        id = body_data.get("id", None)
        name = body_data.get("name", "")
        phone = body_data.get("phone", "")
        sql = "UPDATE USER SET NAME= '%s',PHONE='%s' WHERE ID = %s" % (name, phone, id)
        print(sql, 'sql')
        try:
            cursor.execute(sql)
            db.commit()
            self.write(
                json.dumps({
                    "status": 200,
                    "message": '更新成功'
                })
            )
        except Exception:
            db.rollback()
            self.write(
                json.dumps({
                    "status": 400,
                    "message": '更新失败'
                })
            )
        self.finish()
        db.close()