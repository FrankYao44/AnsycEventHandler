from functools import reduce
SEPARATOR = '^#$'


def code(function_name, kwargs_dict):
    return function_name + SEPARATOR + \
           reduce(lambda a, b: SEPARATOR + a + SEPARATOR + b, [k + v for k, v in kwargs_dict.items()])


def recode(coded_str):
    splited_list = coded_str.split(SEPARATOR)
    function_name = splited_list[0]
    if len(splited_list) == 1:
        return function_name, {}
    else:
        kwargs_dict = {}
        for i in range((len(splited_list)-1)/2):
            kwargs_dict[splited_list[2*i]] = splited_list[2*i + 1]
        return function_name, kwargs_dict