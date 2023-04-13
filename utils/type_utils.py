from utils.log import log_d


def get_type_name(obj):
    return type(obj).__name__


def is_type(obj, type_name: str):
    return get_type_name(obj) == type_name


def is_list(obj):
    return get_type_name(obj) == 'list'


def is_array(obj):
    return is_list(obj)


def check_type(obj, type_name: str, param_name: str = None):
    param_str = 'Parameter' if param_name is None else f"Parameter '{param_name}'"
    if not is_type(obj, type_name):
        raise TypeError(f"{param_str} should be a '{type_name}', got '{get_type_name(obj)}'")


def to_float(val):
    try:
        f_val = float(val)
    except (TypeError, ValueError) as e:
        # log_e('to_float', 'cast', e)
        raise ValueError(f"could not convert value into a float: '{val}'")
    return f_val


if __name__ == '__main__':
    log_d('Utils', 'to_float 456', to_float("456"))
    log_d('Utils', 'to_float toto', to_float("toto"))
