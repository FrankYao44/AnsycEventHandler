from PandoraHub.decorator import dictionary_connector
from PandoraHub.communicate import *


@dictionary_connector('test *', ())
async def test_sth(sth):
    print(sth, ' is tested')
    return
