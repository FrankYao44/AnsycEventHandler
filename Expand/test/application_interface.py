import threading, time, sys, asyncio, hashlib
from function_library import *
from aiohttp import web
from config import config
import json


def recode(w):
    # w.replace('%%syh')
    j = json.loads(w)
    fn_name = j['function_name']
    if fn_name not in globals():
        raise Exception
    fn = globals()[j['function_name']]
    j.pop('function_name')
    r = fn(**j)
    return r

def run_in_process():
    def listener():
        while True:
            r = sys.stdin.read()
            if r:
                my_list.append(r)

    my_list = []
    t = threading.Thread(target=lambda: listener())
    t.start()
    while True:
        for w in my_list:
            r = recode(w)
            sys.stdout.write(r)


def run_in_thread():
    #at first here we expect that test_list should be made up of fn,
    #in other word, lambda: fn(**kwargs)
    #however if we do so, it will be quite different from other two api
    #so I think it should like this:
    #[[fn_name,kwargs].......]
    # now i think json might be ok if the cost could be small
    loop = asyncio.get_event_loop()
    while True:
        if not loop.test_list:
            w = loop.test_list[0]
            return recode(w)



def run_in_network():
    app = web.Application()
    md5 = hashlib.md5()
    md5.update(('test'+config['salt']).encode('utf-8'))
    ###json
    def handle(request,word):
        app.add_routes([web.get('/%s/{word}' % md5.hexdigest(),lambda: recode(word))])
    t = threading.Thread(target=lambda: web.run_app(app))
    t.start()
