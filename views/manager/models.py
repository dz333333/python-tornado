from libs.base.model import BaseModel


class BrandManagerModal(BaseModel):

    def __init__(self, handler, brand_id=None, brand_manager_id=None):
        super(BrandManagerModal, self).__init__(handler)
        self.handler = handler
        self.brand_id = brand_id
        self.brand_manager_id = brand_manager_id
        self.data = {}

    async def fetch_info(self):
        selects = "*"
        await self.db.select("brand_manager", selects, {"brand_id": self.brand_id})
        info = self.db.fetchall()
        data_list = []
        for item in info:
            data_list.append(int(item.get('manager_id')))

        await self.db.select("user", "*", {"id": self.brand_id})
        sql2 = "SELECT * FROM USER WHERE ID IN %s"
        await self.db.execute(sql2, (data_list, ))
        manager_list = self.db.fetchall()
        return self.set_res_info(0, data=manager_list)

    async def insert_info(self, opts):
        insert_data = dict({"brand_id": self.brand_id}, **opts)
        await self.db.insert("brand_manager", insert_data)
        if not self.db.errors:
            await self.db.commit()
        return self.set_res_info(0)

    async def delete_info(self):
        wheres = {"id": self.brand_manager_id}
        await self.db.update("brand_manager", {"valid": 0}, wheres)
        if not self.db.errors:
            await self.db.commit()
        return self.set_res_info(0)
