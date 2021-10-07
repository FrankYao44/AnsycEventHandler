import threading, time, sys, asyncio, hashlib
from Expand.test.function_library import *
from aiohttp import web
from config import config
import json
process_running = False

def executor(w):
    j = json.loads(w)
    fn_name = j['function_name']
    if fn_name not in globals():
        raise Exception
    fn = globals()[j['function_name']]
    j.pop('function_name')
    r = fn(**j)
    sys.stdout.write(str(r))
    return json.dumps(r)


def run_in_process():

    while True:
        r = sys.stdin.read()
        if r:
            break
    try:
        executor(r)

    except Exception as e:
        raise e


def run_in_thread():
    # at first here we expect that test_list should be made up of fn,
    # in other word, lambda: fn(**kwargs)
    # however if we do so, it will be quite different from other two api
    # so I think it should like this:
    # [[fn_name,kwargs].......]
    # now i think json might be ok if the cost could be small
    # however future object is still ...
    # json is not good
    loop = asyncio.get_event_loop()
    while True:
        if loop.thread_queue["test"][0] != []:
            with open("a.txt", "w+") as f:
                f.write(str(loop.thread_queue["test"][0]))
            w = loop.thread_queue["test"][0][0]
            f = w[1]
            if w[0]['function_name'] == "terminate":
                break
            fn = globals()[w[0]['function_name']]
            w[0].pop('function_name')
            r = fn(**w[0])
            w[1].set_result(r)
            loop.thread_queue["test"][0].pop(0)


def process_terminate():
    globals()["process_running"] = False


def run_in_network():
    from aiohttp import web
    app = web.Application()

    def handle(request):
        return web.Response(text=executor(request.match_info['word']))

    def setup_routes(app):
        md5 = hashlib.md5()
        md5.update(('test' + config['salt']).encode('utf-8'))
        app.router.add_get('/%s/{word}' % md5.hexdigest(), handle)

    setup_routes(app)
    web.run_app(app, host='0.0.0.0', port=9000)

if __name__ == "__main__":
    #run_in_process()
    run_in_network()
