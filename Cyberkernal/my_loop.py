import os
import threading
import asyncio
from Cyberkernal.config import config


class EventLoopPolicy(asyncio.DefaultEventLoopPolicy):

    @classmethod
    def start(cls):
        return 0

    dictionary = dict()
    dictionary["start"] = start
    thread_dict = dict()
    thread_queue = dict()
    process_dict = dict()

    def get_event_loop(self):

        try :
            loop = super().get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        loop.dictionary = self.dictionary
        loop.thread_dict = self.thread_dict
        loop.process_dict = self.process_dict
        loop.thread_queue = self.thread_queue
        asyncio.set_event_loop(loop)
        return loop


asyncio.set_event_loop_policy(EventLoopPolicy())

