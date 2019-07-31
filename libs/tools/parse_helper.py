import datetime

from decimal import Decimal


class Parse(object):

    @staticmethod
    def convert_safe(data):
        '''
        desc: 转json前调用, 转为某些json.dumps会报错的数据
        '''
        if data is None:
            return data
        t = type(data)
        if t == tuple:
            return tuple([Parse.convert_safe(e) for e in data])
        elif t == list:
            return [Parse.convert_safe(e) for e in data]
        elif t == dict:
            new_dict = {}
            for key, value in data.items():
                new_dict[Parse.convert_safe(key)] = Parse.convert_safe(value)
            return new_dict
        elif t == datetime.datetime:
            return data.strftime('%Y-%m-%d %H:%M:%S')
        elif t == datetime.date:
            return data.strftime('%Y-%m-%d')
        elif t == datetime.timedelta or t == Decimal:
            return str(data)
        else:
            return data

    @staticmethod
    def remove_none(data):
        if isinstance(data, list) or isinstance(data, tuple):
            new_list = []
            for i in data:
                new_list.append(Parse.remove_none(i))
            data = new_list
        elif isinstance(data, dict):
            new_dic = {}
            for key in data:
                new_dic[key] = Parse.remove_none(data[key])
            data = new_dic
        elif data is None:
            data = ""
        return data
