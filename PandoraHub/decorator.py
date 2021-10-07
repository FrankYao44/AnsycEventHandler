import asyncio
import inspect
import warnings
import functools
from Cyberkernal.CyberException import ConditionWrongException


def dictionary_connector(sentence_pattern, results):
    # in this function , we did such: use attr_name to compare with args, then unite to a dictionary post to the
    # function. at last add the fn to the dictionary to the cyberkernal dictionary .
    # patient: using this function, you just have to post args in order
    # usually results ordered by time
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        # this function can be used to introspect the func @ed to
        # its args,kwargs name will not be writen, only to told their existence
        # and normal position arg and keyword arg will be pointed whether they are default ,one by one
        # this is simply copy from a function, so please ignore some mistake.
        args_signature = inspect.signature(fn)
        pk_input = {}
        pk_default = {}
        arg = False
        kw = False
        for name, param in args_signature.parameters.items():
            if param.kind == param.POSITIONAL_OR_KEYWORD:
                if param.default is param.empty:
                    pk_input[name] = inspect.Parameter.empty
                else:
                    pk_default[name] = param.default
            elif param.kind == param.VAR_POSITIONAL:
                arg = True
            elif param.kind == param.VAR_KEYWORD:
                kw = True
        fn.kw = kw

        wrapper.args = arg
        wrapper.kw = kw
        wrapper.input = pk_input
        wrapper.default = pk_default
        wrapper.__name__ = fn.__name__
        wrapper.results = results
        a = {result: None for result in results}
        a.update(pk_input)
        wrapper.params = a
        wrapper.decorated = True
        loop = asyncio.get_event_loop()
        loop.dictionary[sentence_pattern] = wrapper
        return wrapper

    return decorator


def to_coroutine(fn):
    # just_to make a condition_judgement_function to a coroutine
    # so we ignore the warning of asyncio.RuntimeWarning
    async def wrapper(*args, **kwargs):
        r = fn(*args, **kwargs)
        if not r:
            return ConditionWrongException

    wrapper.__name__ = fn.__name__
    return wrapper
