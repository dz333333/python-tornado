'''
对配置文件中敏感的项，进行加密

加密基本思路：
- 先用repr变成str类型
- 以repr的长度，计算出prime
- 以prime，对顺序进行重排列
- base64加密
- 再对顺序进行重排列
'''

import re
import base64


def _expand_ascii(raw, prime=None):
    ''' 利用高等代数中群、环、域中的质数定理
    - 要求传入一个与len(raw)互质的数 '''
    if prime is None:
        prime = _find_prev_prime(len(raw))
        if prime is None:
            prime = _find_next_prime(len(raw))
    buf = [None] * len(raw)
    i = 0
    for ch in raw:
        buf[i] = ch
        i += prime
        i = i % len(raw)
    return "".join(buf)


def _shrink_ascii(cook, prime=None):
    if prime is None:
        prime = _find_prev_prime(len(cook))
        if prime is None:
            prime = _find_next_prime(len(cook))
    buf = []
    i = 0
    while len(buf) < len(cook):
        buf.append(cook[i])
        i += prime
        i = i % len(cook)
    return "".join(buf)


def encode_object(native_structure, random_salt=None):
    ''' 如果传入了random_salt，回使产生的结果不一样。但不影响decode的结果 '''
    nav_str = repr(native_structure)

    hsh_val = hash(repr(random_salt))  # 可能为负数
    hsh_str = str(hsh_val)[-8:]       # 只取8位，因为第9位很容易是1,2
    factor = hsh_val % 100            # [0, 99]
    prime = _find_next_prime(len(nav_str) + factor)
    shf_str = _expand_ascii(nav_str, prime)

    cat_str = str(prime) + "/" + hsh_str + "/" + shf_str

    bas_str = base64.b64encode(cat_str.encode(encoding='utf-8'))
    bas_str = bas_str.decode()

    bas_str = re.sub('[\r\n]', '', bas_str)  # 这个是系统bug么，md5编码中会有换行符

    shr_str = _shrink_ascii(bas_str)
    return shr_str


def decode_object(encode_string):
    ''' 请非常小心的使用decode_object，因为它有eval调用 '''
    bas_str = _expand_ascii(encode_string)

    cat_str = base64.b64decode(bas_str.encode())
    cat_str = cat_str.decode()

    prime, hsh_str, shf_str = cat_str.split('/', 2)
    del hsh_str  # 用不到了
    prime = int(prime)

    nav_str = _shrink_ascii(shf_str, prime)

    # 虽然globals, locals都滞空了，但还是防不了精心设计的hacker
    # 如果global只用{}, 一些builtins的方法还是有效的 e.g. open, import ..
    native_structure = eval(nav_str, {'__builtins__': {'set': set}}, {})

    return native_structure


def detect_vulnerable(text):
    ''' 因为编码会使用到eval，需基本防御可能混入的一些危险的python code '''
    if not text:
        return []
    python_statements = (
        "repr",
        "open",
        "file",
        "system",
        "eval",
        "exec",
        "execfile",
        "__import__")
    regex_list = (
        "|".join([(s + r"\s*\(") for s in python_statements]),
        r"\s*import\s+",
    )
    v_list = []
    for r in regex_list:
        for m in re.finditer(r, text):
            v_list.append(m.group())
    return v_list


def _find_next_prime(num):
    ''' 找到比num大的下一个质数 '''
    while True:
        num += 1
        if _fermat(num):
            break
    return num


def _find_prev_prime(num):
    ''' 找到比num大的下一个质数 '''
    while num > 1:
        num -= 1
        if _fermat(num):
            break
    else:
        return None
    return num


def _fermat(n, a=2):
    ''' 判断是否为质数 '''
    return (_montgomery2(a, n - 1, n) == 1)


def _montgomery(n, p, m):
    if (p == 0):
        return 1
    k = _montgomery(n, p >> 1, m)
    if (p & 0x01 == 0):
        return k * k % m
    else:
        return n * k * k % m


def _montgomery2(n, p, m):
    ''' _montgomery的非递归版本 '''
    k = 1
    n = n % m
    while (p != 1):
        # diff even and odd number,
        # so we cat get smaller max number (half bits)
        if ((p & 0x01) != 0):
            k = (k * n) % m
        n = (n * n) % m
        p = p >> 1
    return (n * k) % m


if __name__ == "__main__":
    a = encode_object("abc123")
    print(a)
    b = decode_object(a)
    print(b)
