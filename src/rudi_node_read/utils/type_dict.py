from typing import Union

from rudi_node_read.utils.log import log_d, log_assert
from rudi_node_read.utils.types import is_type, is_list, get_type_name, is_list_or_dict


def is_dict(obj) -> bool:
    """
    :return: True of input obj is an object, False otherwise
    """
    return is_type(obj, 'dict')


def is_object(obj) -> bool:
    """
    :return: True of input obj is an object, False otherwise
    """
    return is_dict(obj)


def has_key(obj: dict, key_name: str) -> bool:
    """
    :param obj: an object
    :param key_name: the name of the attribute, that we need to ensure the input object has
    :return: True if input object has an attribute with input key name. False otherwise.
    """
    if not is_dict(obj):
        return False
    return key_name in obj.keys() and obj[key_name] is not None


def check_has_key(obj: dict, key_name: str):
    if not has_key(obj, key_name):
        raise AttributeError(f"Property '{key_name}' missing in obj {obj}")


def safe_get_key(obj: dict, *args):
    """
    Offers a way to access an object attribute hierarchy without raising an error if the attribute doesn't exist
    :param obj: an object
    :param args: hierarchy of attributes we need to access.
    :return: None if the operation doesn't succeed. obj['arg1']['arg2']...['argN'] otherwise.
    """
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


def pick_in_dict(obj: dict, props: list[str]):
    """
    From a given object, returns a partial object with only the given attributes
    :param obj: an object
    :param props: the attributes to keep from the input object
    :return:
    """
    return dict((k, obj[k]) for k in props if k in obj)


def is_element_matching_filter(element, match_filter):
    """
    An element is considered to be matching a filter if all the key/value pairs in the filter are found in the element
    :param element: element that is tested
    :param match_filter: object whose key/value pairs must be found in the tested element
    :return: True if the element is matching the filter object
    """
    fun = 'match_filter'
    if element == match_filter:
        return True
    if not is_list_or_dict(element):
        return False
    if is_dict(element):
        if not is_dict(match_filter):
            return False
        for i, (key, val) in enumerate(match_filter.items()):
            if not has_key(element, key) or not is_element_matching_filter(element[key], val):
                return False
        return True
    elif is_list(element):
        if is_dict(match_filter):
            for e in element:
                if is_element_matching_filter(e, match_filter):
                    return True
            return False
        elif is_list(match_filter):
            for mf in match_filter:
                if not is_element_matching_filter(element, mf):
                    return False
            return True
        else:
            return match_filter in element
    log_d(fun, 'cannot be here, element is', get_type_name(element))
    return False


def is_one_of_elements_matching_filter(elements: list[dict], search_filter: dict):
    for element in elements:
        if is_element_matching_filter(element, search_filter):
            return True
    return False


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
    log_d('Utils', 'filter_list', log_assert(filter_dict_list(a_list, a_filter)))
    log_d('Utils', 'filter_list', log_assert(not filter_dict_list(a_list, b_filter)))

    log_d('Utils', 'is_dict', log_assert(not is_dict(a_list)))
    log_d('Utils', 'is_dict', log_assert(is_dict(b_filter)))
    #
    # o1 = {}
    # o1.update({'e': 'y'})
    # log_d('Utils', 'merge dicts', o1)
    # o1.update({'e': 55})
    # log_d('Utils', 'merge dicts', o1)
    # o1.update({'t': [55]})
    # log_d('Utils', 'merge dicts', o1)
    # o1.update({'t': ['r']})
    # log_d('Utils', 'merge dicts', o1)
    # log_d('Utils', 'items()', o1.items())
    # log_d('Utils', 'keys()', o1.keys())
    # o2 = {'a': 4, 'b': 'oimh', 'c': 'ergomuh', 'd': 5789}
    # log_d('Utils', 'keys()', pick_in_dict(o2, ['b', 'a']))

    elt = {'a': {'b'}, 'c': 3, 'd': {'e': 'f'}}
    etl = {'c': 3, 'd': {'e': 'f'}, 'a': {'b'}}
    eelt = {'a': {'b'}, 'c': 3, 'd': {'e': 'f'}, 't': ['v']}
    log_d('Utils', 'recursive matching 1 (false)', log_assert(not is_element_matching_filter(a_list, b_filter)))
    log_d('Utils', 'recursive matching 2 (true)', log_assert(is_element_matching_filter(elt, etl)))
    log_d('Utils', 'recursive matching 3 (true)', log_assert(is_element_matching_filter(eelt, elt)))

    data_test = {
        'producer': {'organization_id': '1d6bc543-07ed-46f6-a813-958edb73d5f0', 'organization_name': 'SIB (Test)'}}
    filter_test = {'producer': {'organization_name': 'SIB (Test)'}}
    log_d('Utils', 'recursive matching', log_assert(is_element_matching_filter(data_test, filter_test)))
    log_d('Utils', 'recursive matching', log_assert(is_element_matching_filter([data_test], filter_test)))

    data_test2 = {'organization_id': '1d6bc543-07ed-46f6-a813-958edb73d5f0', 'organization_name': 'SIB (Test)'}
    filter_test2 = {'organization_name': 'SIB (Test)'}
    log_d('Utils', 'recursive matching', log_assert(is_element_matching_filter(data_test2, filter_test2)))
    log_d('Utils', 'recursive matching',
          log_assert(is_element_matching_filter({'producer': data_test2}, {'producer': filter_test2})))
    log_d('Utils', 'test matching', log_assert(is_element_matching_filter([5, data_test, 4], [4, data_test])))
    log_d('Utils', 'test matching', log_assert(is_element_matching_filter([5, 4], 5)))
