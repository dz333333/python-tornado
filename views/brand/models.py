from libs.base.model import BaseModel
from libs.tools.widget import Common


class BrandModel(BaseModel):

    def __init__(self, handler):
        super(BrandModel, self).__init__(handler)
        self.handler = handler
        self.data = {}

    async def fetch_list(self, opts):
        """
        获取brandlist
        """
        list_sql, count_sql, values = self._parse_list_sql(opts)
        data_list = await self._fetch_list_data(list_sql, values)
        total_count = await self._total_count(count_sql, values, data_list, opts)
        data = Common.list_model_data(data_list, total_count, opts)
        return self.set_res_info(0, data=data)

    def _parse_list_sql(self, opts):
        sql_base = """
            SELECT *
            FROM brand
            WHERE {where}
            {order} {limit}
        """
        queries, values = [], []
        opts["key_allow"] = [
            ['brand_name', '{key}', 'like'],
            ['valid=1', '{key}', 'raw']
        ]
        opts["order_allow"] = [["brand_name", "{key}"]]
        infos = Common.parse_where(queries, values, opts)
        list_sql = sql_base.format(**infos)
        count_sql = Common.parse_count_sql(infos["where"], sql_base)
        return list_sql, count_sql, values

    async def _fetch_list_data(self, list_sql, values):
        await self.db.execute(list_sql, values)
        data_list = self.db.fetchall()
        return data_list

    async def insert_info(self, opts):
        await self.db.insert("brand", opts)
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
        await self.db.update("brand", {"valid": 0}, wheres)
        if not self.db.errors:
            await self.db.commit()
        return self.set_res_info(0)


class BrandDetailModel(BaseModel):

    def __init__(self, handler, id=None):
        super(BrandDetailModel, self).__init__(handler)
        self.handler = handler
        self.id = id
        self.data = {}

    async def fetch_info(self):
        selects = "*"
        await self.db.select("brand", selects, {"id": self.id})
        info = self.db.fetchone()
        return self.set_res_info(0, data=info)

    async def update_info(self, opts):
        # update
        wheres = {"id": self.id}
        await self.db.update("brand", opts, wheres)
        if not self.db.errors:
            await self.db.commit()
        return self.set_res_info(0)