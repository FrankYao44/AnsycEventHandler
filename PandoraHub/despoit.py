import asyncio
from PandoraHub.decorator import dictionary_connector
import motor

def check_database(device, database, collection):
    name = device + database + collection
    loop = asyncio.get_event_loop()
    if name in loop.connected_database:
        collection = loop.connection_database[name]
    else:
        if device not in configs['device']:
            raise Exception
        client = motor.motor_asyncio.AsyncIOMotorClient(configs['device'][device]['mongodb_address'])
        database = client[database]
        collection = database[collection]
        loop.connection_args[name] = collection
    return collection


@dictionary_connector('just findall * in * of * by *', ('result',))
async def default_findall(condition, collection_name, database, device):
    collection = check_database(device, database, collection_name)
    r = collection.find(condition)
    return [document for document in await r.to_list()]
