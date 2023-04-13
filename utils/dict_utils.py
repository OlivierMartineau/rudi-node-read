from typing import Union

from utils.log import log_d
from utils.type_utils import is_type, is_list


def is_dict(obj):
    return is_type(obj, 'dict')


def is_object(obj):
    return is_dict(obj)


def has_key(obj: dict, key_name: str):
    if not is_dict(obj):
        return False
    return key_name in obj.keys() and obj[key_name] is not None


def check_has_key(obj: dict, key_name: str):
    if not has_key(obj, key_name):
        raise AttributeError(f"Property '{key_name}' missing in obj {obj}")


def safe_get_key(obj: dict, *args):
    if not is_dict(obj):
        return None
    o = obj
    nb_args = len(args)
    for i, key_name in enumerate(args):
        o = o.get(key_name)
        if o is None:
            return None
        if i + 1 == nb_args:
            return o
        if not is_object(o):
            return None


def is_element_matching_filter(element: dict, search_filter: dict):
    """
    An element is considered to be matching a filter if all the key/value pairs in the filter are found in the element
    :param element: element that is tested
    :param search_filter: object whose key/value pairs must be found in the tested element
    :return: True if the element is matching the filter object
    """
    if not is_dict(element):
        return False
    for i, (key, val) in enumerate(search_filter.items()):
        if not has_key(element, key):
            return False
        element_val = element[key]
        if is_dict(element_val) and is_dict(val):
            if not is_element_matching_filter(element_val, val):
                return False
        if is_list(element_val):
            if is_dict(val):
                found_val = False
                for elt_val in element_val:
                    if is_element_matching_filter(elt_val, val):
                        found_val = True
                if not found_val:
                    return False
            if is_list(val):
                for v in val:
                    if is_dict(v):
                        found_val = False
                        for elt_val in element_val:
                            if is_element_matching_filter(elt_val, v):
                                found_val = True
                        if not found_val:
                            return False
                    elif v not in element_val:
                        return False
            else:
                if val not in element_val:
                    return False
        else:
            if element_val != val:
                return False
    return True


def is_element_matching_one_of_filters(element: dict, search_filter: list):
    """
    An element is matching a filter list if it matches at least one of the filters in the filter list.
    An element is considered to be matching a filter if all the key/value pairs in the filter are found in the element
    :param element: element to be tested
    :param search_filter: list of filter objects
    :return: True if the element is matching at least one of the filter object of the filter list
    """
    for i, filter_dict in enumerate(search_filter):
        if is_element_matching_filter(element, filter_dict):
            return True
    return False


def filter_dict_list(searched_list: list, search_filter: Union[dict, list[dict]]) -> list:
    """
    Filter the elements of a list with a given filter object.
    If the filter is a list of filter objects, a list element is kept if it matches at least one of the filter
    objects.
    An element matches a filter objects if its properties match every key/value pair in the filter.
    :param searched_list: a list to filter
    :param search_filter: a filter object or a list of filter object
    :return:
    """
    found_elements = []
    if is_dict(search_filter):
        for element in searched_list:
            if is_dict(search_filter):
                if is_element_matching_filter(element, search_filter):
                    found_elements.append(element)
            elif is_type(search_filter, 'list'):
                if is_element_matching_one_of_filters(element, search_filter):
                    found_elements.append(element)
    return found_elements


def find_in_dict_list(searched_list: list, search_filter: dict):
    """
    Returns the first element in list that matches the input filter.
    None otherwise
    :param searched_list:
    :param search_filter:
    :return: the first element in list that matches the input filter. None otherwise.
    """
    for element in searched_list:
        if is_element_matching_filter(element, search_filter):
            return element
    return None


if __name__ == '__main__':
    log_d('Utils', 'safe_get_key', {'1': 'toto'}, ['1'], '=>', safe_get_key({'1': 'toto'}, '1'))
    log_d('Utils', 'safe_get_key', {'1': 'toto'}, ['2'], '=>', safe_get_key({'1': 'toto'}, '2'))
    log_d('Utils', 'safe_get_key', {"1": {"2": {"3": {"4": 'toto'}}}}, ['1', '2', '3', '4'], '=>',
          safe_get_key({"1": {"2": {"3": {"4": 'toto'}}}}, '1', '2', '3', '4'))

    a_list = [{'cele': 'ri', 'pot': 'ato'}, {'cele': 'riss', 'pot': 'atos'}, {'celse': 'riss', 'pot': 'atos'}]
    a_filter = {'cele': 'ri', 'pot': 'ato'}
    b_filter = {'ele': 'ri', 'pot': 'ato'}
    log_d('Utils', 'filter_list', filter_dict_list(a_list, a_filter))
    log_d('Utils', 'filter_list', 'KO' if filter_dict_list(a_list, b_filter) else 'OK')

    elt = {'a': {'b'}, 'c': 3, 'd': {'e': 'f'}}
    log_d('Utils', 'recursive matching 1 (false)',
          'KO' if is_element_matching_filter(a_list, b_filter) else 'OK')
    log_d('Utils', 'recursive matching 2 (true)',
          'OK' if is_element_matching_filter({'a': {'b'}, 'c': 3, 'd': {'e': 'f'}}, elt) else 'KO')
    log_d('Utils', 'recursive matching 3 (true)',
          'OK' if is_element_matching_filter({'a': {'b'}, 'c': 3, 'd': {'e': 'f'}, 't': ['v']}, elt) else 'KO')
    log_d('Utils', 'is_dict', 'KO' if is_dict(a_list) else 'OK')
    log_d('Utils', 'is_dict', 'OK' if is_dict(b_filter) else 'KO')
