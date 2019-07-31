from libs.base.model import BaseModel


class LoginModel(BaseModel):

    def __init__(self, handler):
        super(LoginModel, self).__init__(handler)
        self.handler = handler
        self.data = {}

    async def start(self, opts):
        """
        登录
        """
        selects = ["name", "password"]
        wheres = {"name": opts["name"], "valid": 1}
        await self.db.select("user", selects, wheres)
        data = self.db.fetchone()
        if data and data["password"] == opts["password"]:
            return self.set_res_info(0, data={"auth_token": ''})
        return self.set_res_info(4007)
