from tornado.log import gen_log

from libs.enums.response_status import ResStatus
from libs.tools.widget import Common


class BaseModel(object):

    def __init__(self, handler):
        super(BaseModel, self).__init__()
        self.db = None  # 默认数据库
        self.redis = None  # 默认Redis
        self.all_user = {}  # 默认存放所有缓存的用户信息
        self.handler = handler
        self.form_data = getattr(handler, "form_data", None)
        self.user = getattr(handler, "user", None)
        self.user_id = self.user["user_id"] if self.user else None
        self._set_db()
        # self._set_redis()
        self.logger = gen_log  # debug|info|warning|error
        self.response_info = {'status': 0, 'message': 'success', 'data': {}}

    def _set_db(self):
        for db_key in self.handler.db_conns:
            setattr(self, db_key, self.handler.db_conns[db_key])

    # def _set_redis(self):
    #     for redis_key in self.handler.redis_conns:
    #         setattr(self, redis_key, self.handler.redis_conns[redis_key])

    def set_res_info(self, status, message=None, data=None):
        message = message if message else ResStatus.get(status)
        self.response_info.update({'status': status, 'message': message})
        if data is not None:
            self.response_info.update({"data": data})
        return self.response_info

    async def commit_or_rollback(self, dbs=None, opts=None):
        '''
        对于简单操作, 可以用此方法自动进行commit或rollback
        对于在commit或rollback之后做额外操作的, 此方法不适用, 需要单独编写
        :dbs -> list, 需要自动操作的数据库对象, 默认为 [self.db, self.db_family]
            e.g. dbs = [self.db, self.db_family]
        :opts -> dict
            :e_status -> int, 错误状态码
            :e_msg -> str, 错误信息
            :e_data -> dict, 错误返回数据
            :s_status -> int, 成功状态码
            :s_msg -> str, 成功信息
            :s_data -> dict, 成功返回数据
        '''
        dbs = dbs or [self.db]
        opts = opts or {}
        error = True if [db.errors for db in dbs if db.errors] else False
        if error:
            for db in dbs:
                await db.rollback()
            status = opts.get("e_status", 5002)
            msg = opts.get("e_msg")
            data = opts.get("e_data")
        else:
            for db in dbs:
                await db.commit()
            status = opts.get("s_status", 0)
            msg = opts.get("s_msg")
            data = opts.get("s_data")
        self.set_res_info(status, msg, data)

    async def _total_count(self, count_sql, values, data_list, opts):
        length = len(data_list)
        page, limit = int(opts.get("page")), int(opts.get("limit"))
        if length < limit:
            total_count = limit * (page - 1) + length
        else:
            await self.db.execute(count_sql, values)
            total_count = self.db.fetchone().get("total")
        return total_count

    def fill_create_info(self, data):
        """填充创建人、创建时间、初始信息状态
        :data -> dict, 待填充的数据体
        """
        data.update({
            "create_by": self.user_id,
            "create_time": Common.current_time(),
            "data_status": 1
        })

    async def update_user_cache(self):
        """
        从数据库拉去最新的用户信息表, 缓存到redis
        :self.all_user -> {"1": {"user_id": 1, "name": "张三"}}
        """
        await self.db.select("auth_user", ["user_id", "name"])
        data = self.db.fetchall()
        self.all_user = {str(user["user_id"]): user for user in data}
        self.redis.set("user_infos", self.all_user, data_type="json")

    async def get_user(self, user_id):
        """
        获取单个用户信息
        output ->
            user_info = {"user_id": 11, "name": "张三"}
        """
        user_id = str(user_id)
        if not self.all_user:
            self.all_user = self.redis.get("user_infos", data_type="json") or {}
        user_info = self.all_user.get(user_id, {})
        if not user_info:
            await self.update_user_cache()
            user_info = self.all_user.get(user_id, {})
        return user_info

    async def get_users(self, data, user_key=["create_by"]):
        """
        批量解析用户信息
        :data -> dict or list
            e.g. {"user_id": 11, "create_by": 22}
            e.g. [{"user_id": 11, "create_by": 22}, {"user_id": 11, "create_by": 22}, ...]
        :user_key -> list, 字典中需要解析用户信息的key
        """
        if isinstance(data, dict):
            for key in user_key:
                data[key] = await self.get_user(data[key])
        elif isinstance(data, list):
            for item in data:
                await self.get_users(item, user_key)
