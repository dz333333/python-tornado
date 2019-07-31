from tormysql.cursor import DictCursor

# 开发环境 DEV-本地, TEST-测试, PRO-正式
env = "TEST"

debug = True
# 是否在log中打印sql语句
sql_print = False
# 是否全局启用请求缓存
open_cache = True

port = 80
host = 'yolo-test.euphonyqr.com'

# 是否发送微信、邮件
send_msg = True

# 管理员邮箱, 接收error邮件
admin_email = ['developer@euphonyqr.com']
# error邮件标题前缀
email_subject_prefix = '[TornadoExample-Test]'

# 是否允许JS跨域调用
remote_access = True

# jwt 私钥 & 过期时间(s)
jwt_secret = '7Ejg0LaHJJr4pHsu'
web_jwt_exp = 60 * 60 * 2

# 数据库配置
db_confs = {
    'db': dict(
        # engine='mysql',
        max_connections=100,  # max open connections
        idle_seconds=300,  # default=7200
        wait_connection_timeout=100,  # wait connection timeout
        host="gz-cdb-o2o7mrrf.sql.tencentcdb.com",
        port=62379,
        db="tornado_example",
        user="tornado_example",
        passwd="objCode:NK10cCVUQnMXeUp2JvAzM2ITNycDMvMD",
        charset="utf8mb4",
        cursorclass=DictCursor
    )
}

# Redis配置
redis_confs = {
    'redis': dict(host='redis', port=6379, db=9, max_connections=100)
}

# 邮箱配置
email_confs = {
    'qy_qq': dict(
        address='smtp.exmail.qq.com',
        port='465',
        account='public@euphonyqr.com',
        passwd='objCode:MnEjJ2kTa3AzMwczYxIDMvAza0IjM=kTUvgD'
    )
}
