import re
import time
import json
import hashlib
import datetime
from decimal import Decimal


class Common(object):

    @staticmethod
    def parse_where(queries, values, opts):
        """
        拼装并生成 由AND组成的where_str, 和limit_str
        :queries -> list, 包含%s的where语句, 与values一一对应
        :values -> list, 存放sql中需要替换%s的value
        :opts -> dict
            :opts["key_allow"] -> list, 允许筛选的字段列表, 及方式
                e.g. [
                    [raw_key, target_key, mode],
                    ['ProvinceID', 'S.{key}'],
                    ['StoreName', 'S.{key}', 'like'],
                    ['StartDate', 'S.{key}', 'les'],
                ]
                :raw_key -> 必填, api传入参数名称
                :target_key -> 选填, 默认'{key}', sql中查询的字段名称
                    如果包含'{key}' -> '{key}'.format(key=raw_key)
                :mode -> 选填, 默认'equal', 查询方式
            :opts["order"] -> str, 前端请求的排序字段, 结尾+或无符号代表递增, -代表递减
                e.g. 'StoreID+,StoreName-'
            :opts["order_allow"] -> list, 允许排序的字段列表, 后端事先设定的规则, 只有在列表中的字段允许排序
                e.g. [
                    ['StoreID', 'S.{key}'],
                    ['StoreName', 'S.{key}']
                ]
            :opts["order_default"] -> str, 默认的排序字段, 如果前端没有指定排序规则,
                将使用这个默认排序规则(前提已设置opts["order_allow"])
                e.g. "StoreID+,StoreName-"
            :opts["page"] -> 当前查询页码
            :opts["limit"] -> 每页显示数量
        """
        modes = {
            "equal": "{0}=%s",
            "raw": "{0}",
            "gt": "{0}>%s",
            "ge": "{0}>=%s",
            "lt": "{0}<%s",
            "le": "{0}<=%s",
            "les": "{0}<=%s",  # +23:59:59
            "like": "{0} LIKE %s",
            "in": "{0} IN %s"
        }
        for k in opts["key_allow"]:
            raw_key = k[0]
            tk = k[1] if len(k) == 2 else '{key}'
            target_key = tk.format(key=raw_key) if '{key}' in tk else tk
            mode = k[2] if len(k) == 3 else 'equal'
            if mode == "raw":
                queries.append(raw_key)
            val = opts.get(raw_key)
            if val is None or val == "":
                continue
            queries.append(modes[mode].format(target_key))
            if mode == "like":
                values.append("%{0}%".format(val))
            elif mode == "les":
                if not isinstance(val, str):
                    val = datetime.datetime.strftime(val, '%Y-%m-%d')
                values.append("{0} 23:59:59".format(val[:10]))
            else:
                values.append(val)
        if len(queries) == 0:
            queries.append("1=%s")
            values.append(1)
        where_str = " AND ".join(queries)
        order_str, limit_str = Common._parse_limit_str(opts)
        infos = {
            "where": where_str,
            "order": order_str,
            "limit": limit_str
        }
        return infos

    @staticmethod
    def _parse_limit_str(opts):
        """
        :opts["order"] -> str, 排序字段, 结尾+或无符号代表递增, -代表递减
            e.g. 'StoreID+,StoreName-'
        :opts["order_allow"] -> list, 允许排序的字段列表
            e.g. [
                ['StoreID', 'S.{key}'],
                ['StoreName', 'S.{key}']
            ]
        :opts["order_default"] -> str, 默认的排序字段
            e.g. "StoreID+,StoreName-"
        output
            e.g. " ORDER BY StoreID DESC LIMIT 0, 10"
        """
        order_str = ""
        page, limit = int(opts["page"]), int(opts["limit"])
        limit_str = " LIMIT %s,%s" % ((page - 1) * limit, limit)
        if not opts.get("order_allow"):
            return order_str, limit_str
        order_allow = {}
        for x in opts["order_allow"]:
            x = x * 2 if len(x) == 1 else x
            x[1] = x[1].format(key=x[0]) if "{key}" in x[1] else x[1]
            order_allow[x[0]] = x[1]
        if opts.get("order"):
            order_str = opts.get("order") or ""
        elif opts.get("order_default"):
            order_str = opts.get("order_default") or ""
        orders = []
        for col in order_str.split(","):
            if col.endswith("+") and col[:-1] in order_allow:
                orders.append(order_allow[col[:-1]])
            elif col.endswith("-") and col[:-1] in order_allow:
                orders.append(order_allow[col[:-1]] + " DESC")
            elif col in order_allow:
                orders.append(order_allow[col])
        order_str = (" ORDER BY " + ", ".join(orders)) if orders else ""
        return order_str, limit_str

    @staticmethod
    def list_model_data(datas, total, opts):
        """返回列表数据所需的数据结构
        """
        data = {
            'results': datas,
            'total': total,
            'page': int(opts.get("page")),
            'limit': int(opts.get("limit"))
        }
        return data

    @staticmethod
    def parse_count_sql(where, sql):
        if sql.find("GROUP BY") > 0:
            sql = "SELECT COUNT(*) AS total FROM (%s) AS TEMPTABLE" % sql
        else:
            sql = re.sub(r"SELECT[\s\S]*?FROM", "SELECT COUNT(*) AS total FROM", sql)
        sql = sql.format(where=where, order="", limit="")
        return sql

    @staticmethod
    def md5(temp_str, to_json=False):
        if temp_str is None:
            return ""
        if to_json:
            temp_str = Common.json_dumps(temp_str)
        return hashlib.md5(temp_str.encode(encoding='utf-8')).hexdigest()

    @staticmethod
    def json_dumps(obj, **kwargs):
        obj = Common.flatten_data(obj)
        return json.dumps(obj, **kwargs)

    @staticmethod
    def json_loads(obj, **kwargs):
        data = None
        try:
            data = json.loads(obj, **kwargs)
        except BaseException as e:
            print("[Error][Json load error]", e)
        return data

    @staticmethod
    def flatten_data(obj):
        """将不能json的数据格式化"""
        f = Common.flatten_data
        if obj is None:
            return None
        t = type(obj)
        if t == tuple:
            return tuple([f(e) for e in obj])
        elif t == list:
            return [f(e) for e in obj]
        elif t == dict:
            return {f(key): f(value) for key, value in obj.items()}
        elif t == datetime.datetime:
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif t == datetime.date:
            return obj.strftime('%Y-%m-%d')
        elif t == datetime.timedelta or t == Decimal:
            return str(obj)
        else:
            return obj

    @staticmethod
    def time_line_desc(raw_time):
        """将日期格式化为 x小时前|x分钟前 的格式"""
        if not isinstance(raw_time, datetime.datetime):
            try:
                raw_time = datetime.datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
            except BaseException:
                return raw_time
        now = datetime.datetime.now()
        if now < raw_time:
            now, raw_time = raw_time, now
        raw_date = raw_time.date()
        now_date = now.date()
        if raw_date != now_date:
            gap_date = now_date - raw_date
            days = gap_date.days
            years, mod = divmod(days, 365)
            if years > 0:
                return "%s年前" % years
            else:
                return "%s天前" % days
        gaps = now - raw_time
        seconds = gaps.seconds
        hours = seconds / 3600
        if hours > 0:
            return "%s小时前" % hours
        mins = seconds / 60
        if mins > 0:
            return "%s分钟前" % mins
        return "%s秒前" % seconds

    @staticmethod
    def current_time(need_str=True):
        ''' return current time str '''
        now = datetime.datetime.now()
        if need_str:
            now = datetime.datetime.strftime(now, '%Y-%m-%d %H:%M:%S')
        return now

    @staticmethod
    def timestamp_to_datetime(timestamp):
        dt = None
        if timestamp:
            time_local = time.localtime(int(str(timestamp)[:10]))
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        return dt

    @staticmethod
    def remove_space(s):
        return s.replace(' ', '').replace('\n', '').replace('\t', '') if s else s

    @staticmethod
    def convert_to_int(num):
        return int(num) if num else num

    @staticmethod
    def utf8(data):
        if isinstance(data, (list, tuple)):
            data = [Common.utf8(i) for i in data]
        elif isinstance(data, dict):
            data = {Common.utf8(k): Common.utf8(v) for k, v in data.items()}
        else:
            data = data.decode('utf8') if isinstance(data, bytes) else data
        return data
