import asyncio
from PandoraHub.decorator import dictionary_connector
from Cyberkernal.config import config
import motor.motor_asyncio


def check_database(device, database, collection):
    name = device + '/' + database + '/' + collection
    loop = asyncio.get_event_loop()
    if name in loop.database_dict:
        collection = loop.database_dict[name]
    else:
        if device not in config['device']:
            raise Exception
        client = motor.motor_asyncio.AsyncIOMotorClient(config['device'][device]['mongodb_address'])
        database = client[database]
        collection = database[collection]
        loop.database_dict[name] = collection
    return collection


@dictionary_connector('just findall * in * of * by * to &', ('result',))
async def default_findall(collection_name, database, device, condition):
    collection = check_database(device, database, collection_name)
    r = collection.find(condition)
    return [document for document in await r.to_list(1)]
