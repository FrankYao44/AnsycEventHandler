import asyncio


class EventLoopPolicy(asyncio.DefaultEventLoopPolicy):

    @classmethod
    def start(cls):
        return 0

    dictionary = dict()
    dictionary["start"] = start
    thread_dict = dict()
    thread_queue = dict()
    process_dict = dict()
    session_dict = dict()
    database_dict = dict()

    def get_event_loop(self):

        try :
            loop = super().get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        loop.dictionary = self.dictionary
        loop.thread_dict = self.thread_dict
        loop.process_dict = self.process_dict
        loop.thread_queue = self.thread_queue
        loop.session_dict = self.session_dict
        loop.database_dict = self.database_dict
        asyncio.set_event_loop(loop)
        return loop


asyncio.set_event_loop_policy(EventLoopPolicy())

