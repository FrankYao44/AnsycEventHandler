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
    return json.dumps(r)


def run_in_process():
    globals()["process_running"] = True
    def listener():
        while globals()["process_running"]:
            r = sys.stdin.read()
            if r:
                print(r, "$")
                my_list.append(r)
                r = ''
        # my_list.append("{\"function_name\":\"calc\", \"num\":233}")
        # time.sleep(1)
        # my_list.append("{\"function_name\":\"process_terminate\"}")

    my_list = []
    t = threading.Thread(target=lambda: listener())
    t.start()
    while globals()["process_running"]:
        if my_list:
            # print(my_list, "$")
            w = my_list[0]
            my_list.pop(0)
            r = executor(w)
            #sys.stdout.write(r)
            #sys.stdout.write("$")

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
    print("www$")
    globals()["process_running"] = False

def run_in_network():
    app = web.Application()
    md5 = hashlib.md5()
    md5.update(('test' + config['salt']).encode('utf-8'))
    routes = web.RouteTableDef()

    @routes.get('/%s/{word}' % md5.hexdigest())
    def handle(request, word):
        return web.Response(text=executor(word))
    t = threading.Thread(target=lambda: web.run_app(app))
    t.start()


if __name__ == "__main__":
    run_in_process()
