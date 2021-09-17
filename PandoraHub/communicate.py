import asyncio, aiohttp
from asyncio import tasks

from PandoraHub.decorator import dictionary_connector
from Cyberkernal.config import config
import hashlib
import json

def code(fn, kwargs):
    j =  json.dumps({'function_name':fn, **kwargs})
    # w = j.replace('\"', '%%syh')
    # j = w.replace(':', '%%mh')
    return j


class NewProcess(asyncio.subprocess.Process):
    async def communicate_one(self, input=None):
        if input is not None:
            stdin = self._feed_stdin(input)
        else:
            stdin = self._noop()
        if self.stdout is not None:
            stdout = self._read_stream(1)
        else:
            stdout = self._noop()
        if self.stderr is not None:
            stderr = self._read_stream(2)
        else:
            stderr = self._noop()
        stdin, stdout, stderr = await tasks.gather(stdin, stdout, stderr,
                                                   loop=self._loop)
        return (stdout, stderr)


asyncio.subprocess.Process = NewProcess

def url_create(main_url, expand, js):
    h = hashlib.md5()
    h.update((expand + config['salt']).encode('utf-8'))
    return main_url + h.hexdigest() + '/' + js + ''


@dictionary_connector('network for * init', ())
def network_init(address):
    loop = asyncio.get_event_loop()
    if not getattr(loop.__dict__, 'SEM', False):
        loop.SEM = asyncio.Semaphore(config['sem_number'])
    loop.connected_network[address] = aiohttp.ClientSession()


@dictionary_connector('network for * close', ())
async def network_close(address):
    loop = asyncio.get_event_loop()
    if address not in loop.connected_network:
        raise Exception
    await loop.connected_network[address].close()


@dictionary_connector('just get from *', ())
async def base_network_communicate_get(url):
    loop = asyncio.get_event_loop()
    async with loop.SEM:
        async with loop.client_session as session:
            resp = await session.get(url,
                                     cookies=config['cookies'],
                                     timeout=config['timeout'],
                                     headers=config['headers'])
            assert resp.status == 200
            r = await resp.content.read(config['read_size'])
            chuck = await resp.content.read(config['read_size'])
            assert not chuck
            return r


@dictionary_connector('just run in process * of * with *', ('result',))
async def default_run_in_process_expand(fn_name, expand_name, kwargs_dict):
    loop = asyncio.get_event_loop()
    r = code(fn_name, kwargs_dict)
    p = asyncio.create_subprocess_shell('python %s' % expand_name,
                                    stdin=asyncio.subprocess.PIPE,
                                    stdout=asyncio.subprocess.PIPE,
                                    stderr=asyncio.subprocess.PIPE)
    result = await p.communicate_one(r)
    await p.wait()
    # equal to p.communicate(r)
    return result


@dictionary_connector('just run in threading * of * with *', ('result',))
async def default_run_in_thread_expand(fn_name, expand_name, kwargs_dict):
    loop = asyncio.get_event_loop()
    f = loop.create_future()
    r = code(fn_name, kwargs_dict)
    loop.threading_dict[expand_name] += (r, f)
    result = await f
    return result


@dictionary_connector('just run in network * of * with *', ('result',))
async def default_run_in_network_expand(fn_name, expand_name, kwargs_dict):
    loop = asyncio.get_event_loop()
    url = url_create(expand_name, code(fn_name, kwargs_dict))
    result = await base_network_communicate_get(url)
    return result
