import re


def to_string(value, default=''):
    return_value = default
    if value is None:
        return default
    else:
        if isinstance(value, (list, tuple)) and len(value) == 1:
            return_value = str(value[0])
        elif isinstance(value, (list, tuple)) and len(value) == 0:
            return_value = default
        else:
            try:
                return_value = str(value)
            except ValueError:
                return_value = default
    return return_value
    pass


def extract_pure_text(text: str):
    """去除字符串中的空白字符"""
    # 替换掉不带标签的words中的空格和换行等
    words = re.sub('\s', '', text)
    words = re.sub('\xa0', '', words)
    words = re.sub('\u3000\u3000', '', words)
    return words
