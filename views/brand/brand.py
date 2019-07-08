import pymysql
from base.base_request.base_handler import BaseHandler
import json
from base.date_encoder import DateEncoder
import tornado


class BrandListHandle(BaseHandler):
    def get(self):
        db = pymysql.connect("localhost", "root", "password",
                             "test", cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        page = self.get_argument("page", '0')
        limit = self.get_argument("limit", '10')
        brnad_name = self.get_argument('brand_name', '')
        sql = f"SELECT * FROM BRAND WHERE BRAND_NAME LIKE '%{brnad_name}%' \
           AND NOT VALID = 0  Limit {int(limit)} OFFSET {int(page)*int(limit)}"
        print(sql, 'sql')
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.execute("SELECT count(*) as total FROM BRAND WHERE NOT \
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
        name = body_data.get("brand_name", "")
        category = body_data.get("brand_category", "")
        img = body_data.get("brand_img", "")
        if name and category:
            sql = f"INSERT INTO BRAND(BRAND_NAME, BRAND_CATEGORY, IMG) VALUES('{name}',\
                '{category}','{img}')"
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
                    "message": "请填写品牌名称和品牌类别"
                })
            )

    def delete(self):
        db = pymysql.connect("localhost", "root", "password", "test")
        cursor = db.cursor()
        body_data = tornado.escape.json_decode(self.request.body)
        id = body_data.get("id", [])
        sql = "UPDATE BRAND SET VALID=0 WHERE ID IN %s"
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


class BrandDetailHandle(BaseHandler):
    def get(self, brand_id):
        db = pymysql.connect("localhost", "root", "password",
                             "test", cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        sql = f"SELECT * FROM BRAND WHERE ID ={brand_id}"
        print(sql, 'sql')
        cursor.execute(sql)
        detail = json.loads(json.dumps(cursor.fetchone(), cls=DateEncoder))
        self.write(json.dumps({
            "status": 200,
            "data": detail
        }))

    def put(self, brand_id):
        db = pymysql.connect("localhost", "root", "password",
                             "test", cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        body_data = tornado.escape.json_decode(self.request.body)
        name = body_data.get("brand_name", "")
        category = body_data.get("brand_category", "")
        img = body_data.get("brand_img", "")
        city = body_data.get("city", "")
        address = body_data.get("address", "")
        if name and category and city and address:
            sql = f"UPDATE BRAND SET brand_name='{name}', brand_category='{category}',\
                img='{img}', city='{city}', address='{address}'\
                WHERE ID = {brand_id}"
            print(sql, 'sql')
            cursor.execute(sql)
            try:
                cursor.execute(sql)
                db.commit()
                self.write(json.dumps({
                    "status": 200,
                    "message": "编辑成功"
                }))
            except Exception:
                db.rollback()
                self.write(
                    json.dumps({
                        "status": 400,
                        "message": '编辑错误'
                    })
                )
            self.finish()
            db.close()
        else:
            self.write(json.dumps({
                "status": 400,
                "message": "请填写所有必填字段"
            }))


class ManagerHandle(BaseHandler):
    def get(self):
        db = pymysql.connect("localhost", "root", "password",
                             "test", cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        sql = f"SELECT id,name FROM user"
        print(sql, 'sql')
        cursor.execute(sql)
        data = cursor.fetchall()
        data_list = []
        for item in data:
            data_list.append(item)
        self.write(
                json.dumps({
                    "status": 200,
                    "data": data_list
                })
            )
        self.finish()
        db.close()


class BrandManagerHandle(BaseHandler):
    def get(self, brand_id):
        db = pymysql.connect("localhost", "root", "password",
                             "test", cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        sql = f"SELECT * FROM BRAND_MANAGER WHERE BRAND_ID ={brand_id}"
        cursor.execute(sql)
        data = cursor.fetchall()
        data_list = []
        for item in data:
            print(item.get('manager_id'), 'append')
            data_list.append(int(item.get('manager_id')))
        sql2 = "SELECT * FROM USER WHERE ID IN %s"
        print(*data_list, 'list')
        cursor.execute(sql2, (data_list, ))
        manager_list = cursor.fetchall()
        for index in range(len(manager_list)):
            manager_list[index] = json.loads(
                json.dumps(manager_list[index], cls=DateEncoder))
        self.write(
                json.dumps({
                    "status": 200,
                    "data": manager_list
                })
            )
        self.finish()
        db.close()

    def post(self, brand_id):
        db = pymysql.connect("localhost", "root", "password",
                             "test", cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        body_data = tornado.escape.json_decode(self.request.body)
        id = json.dumps(body_data.get("id", ''))
        if id:
            sql = f"INSERT INTO BRAND_MANAGER(BRAND_ID,MANAGER_ID) VALUES\
                 ({brand_id},{id})"
            cursor.execute(sql)
            db.commit()
            self.write(
                json.dumps({
                    "status": 200,
                    "message": "操作成功"
                })
            )
            self.finish()
        else:
            self.write(
                json.dumps({
                    "status": 400,
                    "message": "请选择管理员"
                })
            )

    def delete(self, brand_id):
        db = pymysql.connect("localhost", "root", "password",
                             "test", cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        body_data = tornado.escape.json_decode(self.request.body)
        user_id = json.dumps(body_data.get("user_id", ''))
        sql = "DELETE FROM brand_manager WHERE brand_id= %s AND manager_id=%s" % (brand_id, user_id)
        cursor.execute(sql)
        db.commit()
        self.write(
                json.dumps({
                    "status": 200,
                    "message": "删除成功"
                })
            )