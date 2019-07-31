from tormysql.cursor import DictCursor

# 开发环境 DEV-本地, TEST-测试, PRO-正式
env = "PRO"

debug = False
# 是否在log中打印sql语句
sql_print = False
# 是否全局启用请求缓存
open_cache = True

port = 80
host = 'yolo.euphonyqr.com'

# 是否发送微信、邮件
send_msg = True

# 管理员邮箱, 接收error邮件
admin_email = ['developer@euphonyqr.com']
# error邮件标题前缀
email_subject_prefix = '[TornadoExample-Pro]'

# 是否允许JS跨域调用
remote_access = True

# jwt 私钥 & 过期时间(s)
jwt_secret = 'TcsfpRvQps2JVofr'
web_jwt_exp = 60 * 60 * 2

# 数据库配置
db_confs = {
    'db': dict(
        # engine='mysql',
        max_connections=100,  # max open connections
        idle_seconds=300,  # default=7200
        wait_connection_timeout=100,  # wait connection timeout
        host="sh-cdb-ofxcd5qm.sql.tencentcdb.com",
        port=63012,
        db="tornado_example",
        user="xxx",
        passwd="objCode:xxx",
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
