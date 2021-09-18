import os
import threading
import asyncio
from config import config


class EventLoopPolicy(asyncio.DefaultEventLoopPolicy):

    @classmethod
    def start(cls):
        return 0

    dictionary = dict()
    dictionary["start"] = start

    def get_event_loop(self):

        loop = super().get_event_loop()
        loop.dictionary = self.dictionary
        asyncio.set_event_loop(loop)
        return loop


asyncio.set_event_loop_policy(EventLoopPolicy())

