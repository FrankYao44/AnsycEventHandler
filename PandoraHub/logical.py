from PandoraHub.decorator import dictionary_connector, to_coroutine
from PandoraHub.communicate import *
import asyncio


@dictionary_connector('test *', ())
async def test_sth(sth):
    await asyncio.sleep(1)
    print(sth, ' is tested')
    return


@dictionary_connector('STARTL', ())
async def a():
    pass


@dictionary_connector("None", ())
async def b():
    pass


@dictionary_connector('test * to &', ("sth", ))
async def test_sth_to_another(arg):
    await asyncio.sleep(0.5)
    return arg**2
