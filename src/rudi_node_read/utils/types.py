from src.rudi_node_read.utils.log import log_d, log_e


def get_type_name(obj):
    return type(obj).__name__


def is_type(obj, type_name: str):
    return get_type_name(obj) == type_name


def is_list(obj):
    return get_type_name(obj) == 'list'


def is_array(obj):
    return is_list(obj)


def is_list_or_dict(obj):
    return get_type_name(obj) in ['dict', 'list']


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
    try:
        x = to_float("toto")
    except ValueError as e:
        log_e('Utils', 'to_float("toto")', e)

    t = list(range(10))
    log_d('List tests', 't', t)
    log_d('List tests', 't[0]', t[0])
    log_d('List tests', 't[1]', t[1])
    log_d('List tests', 't[-1]', t[-1])
    log_d('List tests', 't[3:]', t[3:])
    log_d('List tests', 't[0:-1]', t[0:-1])
    log_d('List tests', 't[1:-1]', t[1:-1])
    log_d('List tests', 't[0:0]', t[0:0])
    log_d('List tests', 't[:-1]', t[:-1])
    log_d('List tests', 't[::-1]', t[::-1])
