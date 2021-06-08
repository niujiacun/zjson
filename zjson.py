"""

    本程序仅是一个JSON反序列化的玩具版程序。

    JSON和Python之间的映射关系如下：
    ———————————————————————
    JSON             Python
    ———————————————————————
    null             None
    true             True
    false            False
    number           float
    string           str
    array            list
    object           dict



"""

__all__ = ["parse", "UnexpectedCharacterError"]


DIGITS = set("0123456789")

ESCAPES = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}

WHITE_SPACES = {"\n", "\t", "\r", " "}


class UnexpectedCharacterError(ValueError):
    def __init__(self, text_obj):
        super().__init__("unexpected character at index %s(line %s): %s" % (text_obj.index, text_obj.line, text_obj.text))


class TextObj:
    def __init__(self, text):
        self.text = text
        self.index = 0  # 保存读取的位置信息
        self.line = 1 # 记录行数，在遇到错误方便定位

    def read(self):
        # 读取下一个字符
        self.index += 1
        # 判断是否已经读取完毕
        if self.index >= len(self.text):
            return ""
        char = self.text[self.index]
        if char == '\n':
            self.line += 1
        return char

    def skip(self):
        # 对于解析函数来说，调用skip可方便的跳过空白字符
        if self.current in WHITE_SPACES:
            char = self.read()
            while char and char in WHITE_SPACES:
                char = self.read()

    def read_slice(self, step):
        # 方便一次性读取多个字符
        start = self.index
        end = start + step
        self.index = end
        if end > len(self.text):
            raise UnexpectedCharacterError(self)
        return self.slice(start, end)

    def slice(self, start, end):
        # 跟read_slice区别在于，slice不消耗下标
        return self.text[start:end]

    @property
    def current(self):
        # 使用描述符来动态获取当前字符
        if self.index >= len(self.text):
            return ""
        return self.text[self.index]


def parse_null(text_obj):
    if text_obj.read_slice(4) != "null":
        raise UnexpectedCharacterError(text_obj)
    return None


def parse_false(text_obj):
    if text_obj.read_slice(5) != "false":
        raise UnexpectedCharacterError(text_obj)
    return False


def parse_true(text_obj):
    if text_obj.read_slice(4) != "true":
        raise UnexpectedCharacterError(text_obj)
    return True


def parse_number(text_obj):
    head = text_obj.index  # 记录开始时的下标

    char = text_obj.current
    # 处理负号
    if char == "-":
        char = text_obj.read()
    # 整数部分有两种形式：0或者1-9后面跟若干数字
    if char == "0":
        char = text_obj.read()
    elif char in DIGITS:
        while char in DIGITS:
            char = text_obj.read()
    else:
        # 如果整数部分不合法，则整个number不合法
        raise UnexpectedCharacterError(text_obj)
    # 小数部分
    if char == ".":
        char = text_obj.read()
        if char not in DIGITS:
            raise UnexpectedCharacterError(text_obj)
        while char in DIGITS:
            char = text_obj.read()
    # 指数部分
    if char == "E" or char == "e":
        char = text_obj.read()
        if char == "+" or char == "-":
            char = text_obj.read()
        if char not in DIGITS:
            raise UnexpectedCharacterError(text_obj)
        while char in DIGITS:
            char = text_obj.read()
    tail = text_obj.index  # 记录结束时的下标
    # 使用内置的float将字符串转化为浮点数
    return float(text_obj.slice(head, tail))


def get_code_point(text_obj):
    # 解析unicode时使用
    h4 = text_obj.read_slice(4)
    try:
        return int(h4, 16)
    except Exception as e:
        raise UnexpectedCharacterError(text_obj)


def parse_string(text_obj):
    if text_obj.current != '"':
        # 必须以双引号开始
        raise UnexpectedCharacterError(text_obj)

    # 考虑到转义字符的存在，这里需要使用list来保存解析到的单个字符，最后使用join函数返回字符串
    # 避免使用字符串的”+“操作，可以提高效率
    cs = []
    text_obj.read()
    while True:
        char = text_obj.current
        if char == "":
            # 判断text是否已经小号完毕
            raise UnexpectedCharacterError(text_obj)
        if char == "\\":
            # 处理转义字符
            char = text_obj.read()
            if char == "u":
                # 处理 Unicode
                text_obj.read()
                code_point = get_code_point(text_obj)
                if 0xD800 <= code_point <= 0xDBFF and text_obj.slice(text_obj.index, text_obj.index+2) == "\\u":
                    # 处理超过0xFFFF的码点
                    text_obj.read_slice(2)
                    low = get_code_point(text_obj)
                    code_point = 0x10000 + (code_point - 0xD800) * 0x400 + (low - 0xDC00)
                cs.append(chr(code_point))
                continue
            if char not in ESCAPES:
                raise UnexpectedCharacterError(text_obj)
            cs.append(ESCAPES[char])
            text_obj.read()
            continue
        elif char == '"':
            # 结束标志
            text_obj.read()
            return "".join(cs)
        else:
            # 普通字符，直接添加到list
            cs.append(char)
            text_obj.read()


def parse_object(text_obj):
    assert text_obj.current == "{"
    result = {}  # 使用dict保存object解析结果
    text_obj.read()
    text_obj.skip()
    char = text_obj.current
    while True:
        if char == "}":
            # 结束标志。主要是为了判断是否为空object
            text_obj.read()
            break
        # 解析 key
        key = parse_string(text_obj)
        text_obj.skip()
        # 解析冒号
        if text_obj.current != ":":
            raise UnexpectedCharacterError(text_obj)
        text_obj.read()
        text_obj.skip()
        # 解析value
        value = parse_value(text_obj)
        text_obj.skip()
        # 添加到dict
        result[key] = value

        char = text_obj.current
        if char == ",":
            # 判断是否还有键值对
            text_obj.read()
            text_obj.skip()
            continue
        elif char == "}":
            # 结束标志
            text_obj.read()
            break
        else:
            raise UnexpectedCharacterError(text_obj)
    return result


def parse_array(text_obj):
    assert text_obj.current == "["
    result = []  # 使用list来保存array解析结果
    text_obj.read()
    text_obj.skip()
    char = text_obj.current
    while True:
        if char == "]":
            # 结束标志。主要是为了判断是否为空array
            text_obj.read()
            break
        value = parse_value(text_obj)
        result.append(value)

        text_obj.skip()

        char = text_obj.current
        if char == ",":
            # 判断是否还有值
            text_obj.read()
            text_obj.skip()
            continue
        elif char == "]":
            # 结束标志
            text_obj.read()
            break
        else:
            raise UnexpectedCharacterError(text_obj)
    return result


def parse_value(text_obj):
    char = text_obj.current
    if char == "n":
        return parse_null(text_obj)
    elif char == "f":
        return parse_false(text_obj)
    elif char == "t":
        return parse_true(text_obj)
    elif char == '"':
        return parse_string(text_obj)
    elif char == "{":
        return parse_object(text_obj)
    elif char == "[":
        return parse_array(text_obj)
    else:
        return parse_number(text_obj)


def parse(text):
    text_obj = TextObj(text)
    text_obj.skip()  # 跳过开始的空白符
    result = parse_value(text_obj)
    text_obj.skip()  # 跳过结束的空白符
    if text_obj.current != "":
        raise UnexpectedCharacterError(text_obj)
    return result
