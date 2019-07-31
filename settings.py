import importlib

import redis
import tormysql
from tornado.options import options

from libs.tools.config_helper import Helper


def init_config():
    options.config = {}
    configs = ["config"]

    for name in configs:
        module_name = 'conf.%s.%s' % (options.settings, name)
        config_module = importlib.import_module(module_name)
        for k in dir(config_module):
            if k.startswith("__"):
                continue
            data = getattr(config_module, k)
            options.config[k] = Helper.parse_config_code(data)


def init_port():
    options.port = options.port or options.config['port']


def init_db_pool():
    db_pools = {}
    db_confs = options.config["db_confs"]
    for name in db_confs:
        db_pools[name] = tormysql.ConnectionPool(**db_confs[name])
    options.config['db_pools'] = db_pools


def init_redis_pool():
    redis_pools = {}
    redis_confs = options.config["redis_confs"]
    for name in redis_confs:
        redis_pools[name] = redis.ConnectionPool(**redis_confs[name])
    options.config['redis_pools'] = redis_pools


init_config()
init_port()
init_db_pool()
# init_redis_pool()
