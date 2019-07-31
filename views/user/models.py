from libs.base.model import BaseModel
from libs.tools.widget import Common


class UserModel(BaseModel):

    def __init__(self, handler):
        super(UserModel, self).__init__(handler)
        self.handler = handler
        self.data = {}

    async def fetch_list(self, opts):
        """
        获取userlist
        """
        list_sql, count_sql, values = self._parse_list_sql(opts)
        data_list = await self._fetch_list_data(list_sql, values)
        total_count = await self._total_count(count_sql, values, data_list, opts)
        data = Common.list_model_data(data_list, total_count, opts)
        return self.set_res_info(0, data=data)

    def _parse_list_sql(self, opts):
        sql_base = """
            SELECT name, phone
            FROM user
            WHERE {where}
            {order} {limit}
        """
        queries, values = [], []
        opts["key_allow"] = [
            ['name', '{key}', 'like'],
            ['phone', '{key}'],
            ['valid=1', '{key}', 'raw']
        ]
        opts["order_allow"] = [["name", "{key}"], ["phone", "{key}"]]
        infos = Common.parse_where(queries, values, opts)
        list_sql = sql_base.format(**infos)
        count_sql = Common.parse_count_sql(infos["where"], sql_base)
        return list_sql, count_sql, values

    async def _fetch_list_data(self, list_sql, values):
        await self.db.execute(list_sql, values)
        data_list = self.db.fetchall()
        return data_list

    async def insert_info(self, opts):
        await self.db.insert("user", opts)
        if not self.db.errors:
            await self.db.commit()
        return self.set_res_info(0)

    async def update_info(self, opts):
        # update
        wheres = {"id": opts["id"]}
        await self.db.update("user", opts, wheres)
        if not self.db.errors:
            await self.db.commit()
        return self.set_res_info(0)

    async def delete_info(self, opts):
        # update
        wheres = {"id": opts["id"]}
        await self.db.update("user", {"valid": 0}, wheres)
        if not self.db.errors:
            await self.db.commit()
        return self.set_res_info(0)