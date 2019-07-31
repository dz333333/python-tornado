from libs.tools import obj_code


class Helper(object):

    @staticmethod
    def parse_config_code(data):
        if isinstance(data, str):
            if data.startswith("objCode:"):
                data = obj_code.decode_object(data.replace("objCode:", "", 1))
        elif isinstance(data, dict):
            for k in data:
                data[k] = Helper.parse_config_code(data[k])
        return data


if __name__ == "__main__":
    # import sys
    # sys.path.append("../..")
    code = [
        'MnMDOvR3J4ETMxIDOlQzMzMncvAD',
        'objCode:MnMDOvR3J4ETMxIDOlQzMzMncvAD',
        {"aa": 'objCode:MnMDOvR3J4ETMxIDOlQzMzMncvAD',
            'bb': 'MnMDOvR3J4ETMxIDOlQzMzMncvAD'}
    ]
    for c in code:
        print(Helper.parse_config_code(c))
