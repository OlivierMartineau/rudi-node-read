from re import compile
from uuid import UUID

from src.rudi_node_read.utils.log import log_d
from src.rudi_node_read.utils.types import is_type


def is_string(s):
    return is_type(s, 'str')


ISO_FULL_DATE_REGEX = compile(
    r'^([\+-]?\d{4})-(\d{2})-(\d{2})T([0-2]\d):([0-5]\d):([0-5]\d)(?:\.(\d{3}))?(?:Z|([\+-][0-5]\d:(?:0|3)0))$')


def is_iso_full_date(date_str):
    return bool(ISO_FULL_DATE_REGEX.match(date_str))


# REGEX_UUID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')


def is_uuid_v4(uuid: str):
    if uuid is None:
        return False
    try:
        uuid_v4 = UUID(str(uuid))
        if uuid_v4.version == 4:
            return uuid_v4
        else:
            return False
    except ValueError as e:
        return False


def validate_uuid_v4(uuid: str):
    try:
        if uuid is not None:
            uuid_v4 = UUID(str(uuid))
            if uuid_v4.version == 4:
                return str(uuid_v4)
    except ValueError:
        pass
    raise ValueError('System ID should be a UUIDv4')


def slash_join(*args):
    """
    Joins a set of strings with a slash (/) between them (useful for merging URLs or paths fragments)
    """
    non_null_args = []
    for frag in args:
        if frag is None or frag == '':
            pass
        else:
            non_null_args.append(frag.strip('/'))
    joined_str = '/'.join(non_null_args)
    return joined_str


if __name__ == '__main__':
    host = 'http://thing.org/'
    path = '/first_level/'
    url = '/second_level/'
    additional_url = '/'
    log_d('slash_join', 'No args', slash_join())
    log_d('slash_join', 'None arg', slash_join(None))
    log_d('slash_join', 'None args', slash_join(None, None, None))
    log_d('slash_join', 'host only', slash_join(host))
    log_d('slash_join', 'host+path', slash_join(host, path))
    log_d('slash_join', 'host+None+path+url', slash_join(host, None, path, url))
    log_d('slash_join', 'host+""+/+None+path+url+//', slash_join(host, '', '/', None, path, url, '//'))
    log_d('slash_join', 'None+path+url', slash_join(None, path, url))
    log_d('slash_join', '/4+None+path+url', slash_join('/4', None, path, url))
    # start = time()
    # for i in range(100000):
    #     slash_join(host, path, rudi_node_url, additional_url, None, None)
    # end = time()
    # print('Time needed:', (end - start)/100000)

    log_d('Utils', 'is_uuid_v4', is_uuid_v4('2fbbafc5-43fe-4859-99a1-19077530e35a'))
    log_d('Utils', 'is_iso_date', is_iso_full_date('2019-05-02T11:30:57+00:00'))
