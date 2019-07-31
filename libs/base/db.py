import re
import copy

from tornado.options import options
from pymysql.err import Error


def utf8(data):
    """将数据转换成UTF8格式
    """
    def _utf8(value):
        return value.decode('utf8') if isinstance(value, bytes) else value
    if isinstance(data, (list, tuple)):
        data = [utf8(i) for i in data]
    elif isinstance(data, dict):
        data = {utf8(k): utf8(v) for k, v in data.items()}
    else:
        data = _utf8(data)
    return data


class BaseDB(object):
    def __init__(self, db_key):
        self.pool = options.config['db_pools'][db_key]
        self.conn = None
        self.cursor = None
        self.execute_status = False
        self.debug = options.config.get("sql_print", False)  # True的时候将打印sql
        self.errors = []

    async def close(self):
        if self.cursor:
            await self.cursor.close()
        if self.conn:
            await self.conn.close()

    async def _get_conn_and_cursor(self):
        if self.conn is None:
            self.conn = await self.pool.Connection()
        if self.cursor is None:
            self.cursor = self.conn.cursor()

    async def rollback(self):
        if self.conn:
            await self.conn.rollback()
            self.execute_status = False

    async def commit(self):
        if self.conn:
            await self.conn.commit()
            self.execute_status = False

    async def execute(self, *args):
        """去掉sql语句中多余的换行和空格
        """
        args = list(args)
        args[0] = " ".join(args[0].replace("\n", " ").split())
        if self.debug:
            if len(args) > 1:
                print((args[0].replace("%s", '"%s"') % tuple(args[1])) + ";")
            else:
                print(args[0] + ";")
        await self._get_conn_and_cursor()
        await self.cursor.execute(*args)
        self.execute_status = True

    async def executemany(self, *args):
        """去掉sql语句中多余的换行和空格
        """
        args = list(args)
        args[0] = " ".join(args[0].replace("\n", " ").split())
        await self._get_conn_and_cursor()
        await self.cursor.executemany(*args)
        self.execute_status = True

    def fetchone(self):
        data = self.cursor.fetchone() or {}
        return data

    def fetchall(self):
        data_list = self.cursor.fetchall()
        return list(data_list)


class DBObject(BaseDB):
    def __init__(self, db_key):
        super(DBObject, self).__init__(db_key)

    async def select(self, tb_name, selects, wheres=None, groups=None, orders=None, limit=None):
        """
        :tb_name -> db table name
        :selects -> list or str, 需要查询的字段
            e.g. ["AA", "BB"] -> SELECT AA, BB FROM ...
            e.g. "*" -> SELECT * FROM ...
                 "Count" -> SELECT COUNT(*) AS Count FROM ...
                 "Count(AA)" -> SELECT COUNT(AA) AS Count FROM ...
        :wheres -> dict, where语句包含的条件, 只支持用AND连接
            e.g. {"CC": 33, "DD": 44} -> WHERE CC=33 AND DD=44 ...
            e.g. {"~CC>": 33, "~DD LIKE": "%44%"} -> WHERE CC > 33 AND DD LIKE "%44%" ...
        :groups -> list, 结果集按照提供的字段分组
            e.g. ["CC", "DD"]
        :orders -> list, 结果集按照提供的字段排序, 结尾默认+代表递增, -代表递减
            e.g. ["CC+", "DD-"]
        :limit -> int, 返回结果集的数量限制
            e.g. 10 -> LIMIT 0, 10
        """
        await self._select(tb_name, selects, wheres, groups, orders, limit)

    async def insert(self, tb_name, values):
        """
        :tb_name -> db table name
        :values -> dict, 需要insert的字段
            e.g. {"AA": 11, "BB": 22} -> ... (AA, BB) VALUES (11, 22) ...
        """
        row_id = await self._insert(tb_name, values)
        return row_id

    async def insert_many(self, tb_name, values):
        """
        :tb_name -> db table name
        :values -> list containe dict
            e.g. [{"AA": 11, "BB": 22}, {"AA": 33, "BB": 44} ...]
        """
        await self._insert(tb_name, values, many=True)

    async def update(self, tb_name, sets, wheres):
        """
        :tb_name -> db table name
        :sets -> dict, 需要update的字段
            e.g. {"AA": 11, "BB": 22} -> SET AA=11, BB=22 ...
        :wheres -> dict, 参考select方法中的wheres
        """
        await self._update(tb_name, sets, wheres)

    async def update_many(self, tb_name, sets, wheres):
        """
        :tb_name -> db table name
        :sets -> list containe dict
            e.g. [{"AA": 11, "BB": 22}, {"AA": 33, "BB": 44} ...]
        :wheres -> list containe dict (dict参考select方法中的wheres)
            e.g. [{"CC": 11, "DD": 22}, {"CC": 33, "DD": 44} ...]
        """
        await self._update(tb_name, sets, wheres, many=True)

    async def delete(self, tb_name, wheres):
        """
        :tb_name -> db table name
        :wheres -> dict, where语句包含的条件
            e.g. {"CC": 11, "DD": 22} -> WHERE CC=11 AND DD=22 ...
        """
        await self._delete(tb_name, wheres)

    async def delete_many(self, tb_name, wheres):
        """
        :tb_name -> db table name
        :wheres -> list containe dict
            e.g. [{"CC": 11, "DD": 22}, {"CC": 33, "DD": 44} ...]
        """
        await self._delete(tb_name, wheres, many=True)

    async def _select(self, tb_name, selects, wheres, groups, orders, limit):
        aa, bb, cc = ParseData.for_select(
            selects, wheres, groups, orders, limit)
        info = {
            "selects": aa,
            "tb": tb_name,
            "wheres": bb
        }
        sql = "SELECT {selects} FROM {tb} WHERE {wheres}".format(**info)
        await self.execute(sql, cc)

    async def _insert(self, tb_name, values, many=False):
        aa, bb, cc = ParseData.for_insert(values)
        info = {
            "tb": tb_name,
            "cols": aa,
            "values": bb
        }
        sql = "INSERT INTO {tb} ({cols}) VALUES ({values})".format(**info)
        try:
            if many:
                await self.executemany(sql, cc)
            else:
                await self.execute(sql, cc[0])
                return self.cursor.lastrowid
        except Exception as e:
            self._db_error(e)

    async def _update(self, tb_name, sets, wheres, many=False):
        aa, bb, cc = ParseData.for_update(sets, wheres)
        info = {
            "tb": tb_name,
            "sets": aa,
            "wheres": bb
        }
        sql = "UPDATE {tb} SET {sets} WHERE {wheres}".format(**info)
        try:
            if many:
                await self.executemany(sql, cc)
            else:
                await self.execute(sql, cc[0])
        except Exception as e:
            self._db_error(e)

    async def _delete(self, tb_name, wheres, many=False):
        aa, cc = ParseData.for_delete(wheres)
        info = {
            "tb": tb_name,
            "wheres": aa
        }
        sql = "DELETE FROM {tb} WHERE {wheres}".format(**info)
        try:
            if many:
                await self.executemany(sql, cc)
            else:
                await self.execute(sql, cc[0])
        except Exception as e:
            self._db_error(e)

    def _db_error(self, e):
        """
        :e -> (1062, u"Duplicate entry 'rick' for key 'name'")
            e[0] = 1062 -> Insert duplicate
            e[0] = 1451 -> Cannot delete: a foreign key constraint fails
        output
            errors = [{
                "err_num": 1062,
                "err_str": "Duplicate entry 'rick' for key 'name'",
                "err_key": 'name',
                "err_val": 'rick'
            }]
        """
        if not isinstance(e, Error):
            assert hasattr(e, "value")
            return e.value
        elif e.args[0] == 1062:
            group = re.findall(r"'([^']*?)'", e.args[1])
            self.errors.append({
                "err_num": e.args[0],
                "err_str": e.args[1],
                "err_key": group[1],
                "err_val": group[0]
            })
        elif e.args[0] == 1451:
            self.errors.append({
                "err_num": e.args[0],
                "err_str": e.args[1]
            })
        else:
            raise e


class ParseData(object):
    @staticmethod
    def for_select(selects, wheres=None, groups=None, orders=None, limit=None):
        """
        :selects -> list or str, 需要查询的字段
            e.g. ["AA", "BB"] -> SELECT AA, BB FROM ...
            e.g. "*" -> SELECT * FROM ...
                 "Count" -> SELECT COUNT(*) AS Count FROM ...
                 "Count(AA)" -> SELECT COUNT(AA) AS Count FROM ...
        :wheres -> dict, where语句包含的条件, 只支持用AND连接
            e.g. {"CC": 33, "DD": 44} -> WHERE CC=33 AND DD=44 ...
            e.g. {"~CC>": 33, "~DD LIKE": "%44%"} -> WHERE CC > 33 AND DD LIKE "%44%" ...
        :groups -> list, 结果集按照提供的字段分组
            e.g. ["CC", "DD"]
        :orders -> 结果集按照提供的字段排序, 结尾默认+代表递增, -代表递减
            e.g. ["CC+", "DD-"]
        :limit -> int, 返回结果集的数量限制
            e.g. 10 -> LIMIT 0, 10
        output
            aa = "AA, BB"
            bb = "CC=%s AND DD=%s ORDER BY CC, DD DESC LIMIT 0, 10"
            cc = [11, 22]
        """
        if isinstance(selects, (list, tuple)):
            aa = ", ".join(selects)
        elif selects == "Count":
            aa = "COUNT(*) AS Count"
        elif selects.startswith("Count(") and selects.endswith(")"):
            aa = selects.replace("Count", "COUNT") + "AS Count"
        else:
            aa = selects
        if not wheres:
            wheres = {1: 1}
        bb, cc, dd = [], [], []
        for col, val in wheres.items():
            col = str(col)
            col = (col[1:] + " %s") if col.startswith("~") else (col + "=%s")
            bb.append(col)
            cc.append(val)
        bb = " AND ".join(bb)
        for col in (orders or []):
            if col.endswith("+"):
                col = col[:-1]
            elif col.endswith("-"):
                col = col[:-1] + " DESC"
            dd.append(col)
        dd = (" ORDER BY " + ", ".join(dd)) if dd else ""
        tmp_groups = (" GROUP BY " + ", ".join(groups)) if groups else ""
        dd = tmp_groups + dd
        if isinstance(limit, int) and limit > 0:
            dd += " LIMIT 0, %s" % limit
        bb += dd
        return aa, bb, cc

    @staticmethod
    def for_insert(values):
        """
        :values -> dict or list
            e.g. {"AA": 11, "BB": 22}
            e.g. [{"AA": 11, "BB": 22}, {"AA": 33, "BB": 44} ...]
        output
            aa = "AA, BB"
            bb = "%s, %s"
            cc = [[11, 22], [33, 44]]
        """
        values = ParseData.dict_to_list(values)
        aa = list(values[0].keys())
        bb = ["%s"] * len(aa)
        cc = []
        for group in values:
            cc.append([group.pop(x) for x in aa])
            assert not group
        aa = ", ".join(aa)
        bb = ", ".join(bb)
        return aa, bb, cc

    @staticmethod
    def for_update(sets, wheres):
        """
        :sets -> dict or list
            e.g. {"AA": 11, "BB": 22}
            e.g. [{"AA": 11, "BB": 22}, {"AA": 33, "BB": 44} ...]
        :wheres -> dict or list
            e.g. {"CC": 33, "DD": 44}
            e.g. [{"CC": 55, "DD": 66}, {"CC": 77, "DD": 88} ...]
        output
            aa = "AA=%s, BB=%s"
            bb = "CC=%s AND DD=%s"
            cc = [[11, 22, 33, 44], ...]
        """
        sets = ParseData.dict_to_list(sets)
        wheres = ParseData.dict_to_list(wheres)
        assert len(sets) == len(wheres)
        aa = list(sets[0].keys())
        bb = list(wheres[0].keys())
        cc = []
        for i in range(0, len(sets)):
            m = [sets[i].pop(x) for x in aa]
            n = [wheres[i].pop(x) for x in bb]
            assert not sets[i]
            assert not wheres[i]
            cc.append(m + n)
        aa = ", ".join([(x + "=%s") for x in aa])
        bb = " AND ".join([(x + "=%s") for x in bb])
        return aa, bb, cc

    @staticmethod
    def for_delete(wheres):
        """
        :wheres -> dict or list
            e.g. {"CC": 11, "DD": 22}
            e.g. [{"CC": 11, "DD": 22}, {"CC": 33, "DD": 44} ...]
        output
            aa = "CC=%s AND DD=%s"
            cc = [[11, 22], [33, 44], ...]
        """
        wheres = ParseData.dict_to_list(wheres)
        aa = list(wheres[0].keys())
        cc = []
        for group in wheres:
            cc.append([group.pop(x) for x in aa])
            assert not group
        aa = " AND ".join([(x + "=%s") for x in aa])
        return aa, cc

    @staticmethod
    def dict_to_list(data):
        d = copy.deepcopy(data)
        d = [d] if isinstance(d, dict) else d
        return d


if __name__ == "__main__":
    # select_info = {
    #     "selects": "Count",
    #     # "selects": ["AA", "BB"],
    #     "wheres": {"~CC>": 33, "~DD LIKE ": "%44%"},
    #     "groups": ["EE", "FF"],
    #     "orders": ["EE+", "FF-"],
    #     "limit": 20
    # }
    # print(ParseData.for_select(**select_info))

    # values = [{"AA": 11, "BB": 22}, {"AA": 33, "BB": 44}]
    # print(ParseData.for_insert(values))

    # sets = [{"AA": 11, "BB": 22}, {"AA": 33, "BB": 44}]
    # wheres = [{"CC": 55, "DD": 66}, {"CC": 77, "DD": 88}]
    # print(ParseData.for_update(sets, wheres))

    # wheres = [{"CC": 11, "DD": 22}, {"CC": 33, "DD": 44}]
    # print(ParseData.for_delete(wheres))
    pass
