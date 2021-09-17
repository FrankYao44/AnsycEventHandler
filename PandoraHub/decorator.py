import asyncio
import inspect


def dictionary_connector(sentence_pattern, results):
    # in this function , we did such: use attr_name to compare with args, then unite to a dictionary post to the
    # function. at last add the fn to the dictionary to the cyberkernal dictionary .
    # patient: using this function, you just have to post args in order
    # usually results ordered by time
    def decorator(fn):
        def wrapper(**kwargs):
            if tuple(kwargs.keys()) != pk_input & fn.kw != True :
                raise TypeError('%s expected %s arguments, got %s'
                                % (fn.__name__, pk_input + pk_default, list(kwargs.keys())))
            return fn(**dict(**kwargs))

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
        wrapper.args = arg
        wrapper.kwargs = kw
        wrapper.input = pk_input
        wrapper.default = pk_default
        wrapper.__name__ = fn.__name__
        wrapper.results = results
        wrapper.decorated = True
        loop = asyncio.get_event_loop()
        loop.dictionary[sentence_pattern] = wrapper

    return decorator