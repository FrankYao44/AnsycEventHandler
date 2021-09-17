from PandoraHub.decorator import dictionary_connector
from PandoraHub.communicate import *
import asyncio


@dictionary_connector('test *', ())
async def test_sth(sth):
    await asyncio.sleep(1)
    print(sth, ' is tested')
    return
