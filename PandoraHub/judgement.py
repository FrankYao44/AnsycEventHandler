from PandoraHub.decorator import dictionary_connector, to_coroutine


@dictionary_connector("i am right", ())
@to_coroutine
def i_am_right():
    return True


@dictionary_connector("i am wrong", ())
@to_coroutine
def i_am_wrong():
    return False


@dictionary_connector(" one added to one is *", ())
@to_coroutine
def a_math_problem(num):
    if num == 2:
        return True
    else:
        return False

