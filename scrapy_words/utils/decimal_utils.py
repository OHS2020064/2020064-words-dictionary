def to_decimal(value, default=0):
    if value is None:
        return default
    else:
        if isinstance(value, (list, tuple)) and len(value) == 1:
            try:
                return_value = float(value[0])
            except ValueError:
                return_value = default
        elif isinstance(value, (list, tuple)) and len(value) == 0:
            return_value = default
        else:
            try:
                return_value = float(value)
            except ValueError:
                return_value = default
    return return_value
    pass
