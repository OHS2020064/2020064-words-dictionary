
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
