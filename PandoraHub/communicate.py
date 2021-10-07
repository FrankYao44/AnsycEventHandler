import asyncio, aiohttp
import os.path
import threading
from asyncio import tasks
from asyncio.log import logger

from Cyberkernal.config import config
from PandoraHub.decorator import dictionary_connector
from Cyberkernal.config import config
import hashlib
import json


def code(fn, kwargs={}):
    j = json.dumps({'function_name': fn, **kwargs})
    # w = j.replace('\"', '%%syh')
    # j = w.replace(':', '%%mh')
    return j


def url_create(main_url, expand, js):
    h = hashlib.md5()
    h.update((expand + config['salt']).encode('utf-8'))
    return main_url + h.hexdigest() + '/' + js + ''


@dictionary_connector('network for * init', ())
async def network_init(address):
    loop = asyncio.get_event_loop()
    if not getattr(loop.__dict__, 'SEM', False):
        loop.SEM = asyncio.Semaphore(config['sem_number'])
    loop.session_dict[address] = aiohttp.ClientSession()
    print(1)
    await asyncio.sleep(0)


@dictionary_connector('network for * close', ())
async def network_close(address):
    loop = asyncio.get_event_loop()
    if address not in loop.session_dict:
        raise Exception
    await loop.session_dict[address].close()


@dictionary_connector('process for * init', ())
async def process_init(expand_name):
    loop = asyncio.get_event_loop()
    if expand_name not in loop.process_dict:
        loop.process_dict[expand_name] = []
    expand_path = os.path.join(config["path"], "Expand", expand_name, "application_interface.py")
    coro = asyncio.create_subprocess_shell('python %s' % expand_path,
                                           stdin=asyncio.subprocess.PIPE,
                                           stdout=asyncio.subprocess.PIPE,
                                           stderr=asyncio.subprocess.PIPE)
    p = await coro
    if expand_name not in loop.process_dict:
        loop.process_dict[expand_name] = []
    loop.process_dict[expand_name].append(p)


@dictionary_connector('process for * all terminate', ())
async def process_terminate(expand_name):
    loop = asyncio.get_event_loop()
    if expand_name not in loop.process_dict:
        raise KeyError("no expand process named {} running yet".format(expand_name))
    for p in loop.process_dict[expand_name]:
        r = code("process_terminate", {})
        await p.communicate(input=r.encode("UTF-8"))


@dictionary_connector('thread for * init', ())
async def thread_init(expand_name):
    loop = asyncio.get_event_loop()
    if expand_name not in loop.thread_dict:
        loop.thread_dict[expand_name] = []
        loop.thread_queue[expand_name] = []
    fn = __import__('Expand.test.application_interface',
                    fromlist=['{}.application_interface'.format(expand_name)]).run_in_thread
    t = threading.Thread(target=fn)
    loop.thread_dict[expand_name].append(t)
    loop.thread_queue[expand_name].append([])
    t.start()
    await asyncio.sleep(0)


@dictionary_connector('thread for * all terminate', ())
async def thread_terminate(expand_name):
    loop = asyncio.get_event_loop()
    if expand_name not in loop.thread_dict:
        raise KeyError("no running thread named {} running yet".format(expand_name))
    for i in range(len(loop.thread_dict[expand_name])):
        t = loop.thread_dict[expand_name][i]
        if not t.is_alive:
            continue
        else:
            f = loop.create_future()
            loop.thread_queue[expand_name][i].append([{"function_name": "terminate"}, f])
            await f
    loop.thread_dict[expand_name] = []
    loop.thread_queue[expand_name] = []


@dictionary_connector('just get from * to &', ('r',))
async def base_network_communicate_get(url):
    loop = asyncio.get_event_loop()
    async with loop.SEM:
        address = url[:url.find("/", 8)]
        args = url[url.find("/", 8):]
        async with loop.session_dict[address] as session:
            # args = args.replace(":", "a")
            # args = args.replace(",", "a")
            # args = args.replace(" ", "a")
            # args = args.replace("\"", "a")
            # args = args.replace("{", "a")
            # args = args.replace("}", "a")
            # args = args.replace("_", "a")
            resp = await session.get(address+args,
                                     cookies=config['cookies'],
                                     timeout=config['timeout'],
                                     headers=config['headers'])
            assert resp.status == 200
            r = await resp.content.read(config['read_size'])
            chuck = await resp.content.read(config['read_size'])
            # assert not chuck
            return r


@dictionary_connector('just run in process * of * with * to &', ('result',))
async def default_run_in_process_expand(fn_name, expand_name, kwargs_dict):
    loop = asyncio.get_event_loop()
    p = loop.process_dict[expand_name][0]
    r = code(fn_name, kwargs_dict)
    result = await p.communicate(input=r.encode("UTF-8"))
    if result[-1] != b'':
        raise Exception(result[-1].decode("utf-8"))
    else:
        return result[0].decode("utf-8")


@dictionary_connector('just run in thread * of * with * to &', ('result',))
async def default_run_in_thread_expand(fn_name, expand_name, kwargs_dict):
    loop = asyncio.get_event_loop()
    f = loop.create_future()
    r = {"function_name": fn_name}
    r.update(kwargs_dict)
    loop.thread_queue[expand_name][0].append([r, f])
    result = await f
    return result


@dictionary_connector('just run in network * of * with * to &', ('result',))
async def default_run_in_network_expand(fn_name, expand_name, kwargs_dict):
    url = url_create(config["url"], expand_name, code(fn_name, kwargs_dict))
    result = await base_network_communicate_get(url)
    return result
