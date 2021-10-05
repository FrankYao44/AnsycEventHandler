import logging
from CyberException import OrderFailedException, ConditionWrongException
import asyncio

logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')


class NumberVectorMetaclass(type):
    """
    language standard
    1. consist of sentence,separated by \n.
        for example:
            do sth(\n)
            do some other thing (\n)
        sentence , which will translated to standard function key(look below),
        will finally translated to function in dictionary.
        for example  ,the sentence above will be translated to this:
            fn1(__name__==do_sth) fn2 (__name__==do_other_thing)
    2. sentence compose to instruction.
        for accurate, they will be transform to a dictionary which key is N and value is FN type
        for example, the sentence above will be fianlly translated to such:
            {0: FN_object(with fn1 write in the args), 1: FN_object(fn2)}
    3. FN type take the position of arrow,for they all have a later_id list ,which save the id whose fn next to be run.
        for example, the sentence above FN type will be like this:
            FN_object.later_id = [0] FN_object.later_id = [1], FN_object.later_id = ["end"], FN_object.later_id = []
        two special FN, "start" and "end", will straightly add to line
        when running ,the function will be called, added to event_loop.
    4. IF language: IF condition1
                    condition2
                    Then do A
                    do B
                    ELIF condition3
                    THEN do C
                    IF condition4
                    THEN do D
                    ENDIF
                    ENDIF
        (try to keep pace with pseudo-code)
    5. the explainer will be like this :
        FN_object.later_id:[0],FN_object.later_id:[1],FN_object.later_id:[2,4],
        FN_object.later_id:[3,2],FN_object.later_id:["END"],FN_object.later_id:[5,"END"],
        FN_object.later_id:[6],FN_object.later_id:[7,"END"],FN_object.later_id:["END",6],FN_object.later_id:[],
        rule: logically in advance(first do,then other option) ;back to nearest judgement point;
    6. restriction
    7. loop
    """

    '''
    more Specifically:
    test *a\n
    IF i am right\n
    i am right\n
    IF i am right\n
    test *b\n
    ENDIF\n
    ENDIF
    {"start":FN(?), 0:FN(fn1), 1:FN(fn2), 2:FN(fn2), 3:FN(f2), 4:FN(fn1), 5: FN()}
    '''

    def __new__(cls, name, bases, attrs):

        class FN:
            def __init__(self, fn, inputer, results):
                self.fn = fn
                self.later_id = []
                self.inputer = inputer
                self.results = results

            def set_later(self, later_id):
                self.later_id.append(later_id)

            def delete_later(self):
                try:
                    self.later_id.pop(0)
                except IndexError as e:
                    raise e

            def __call__(self, *args, **kwargs):
                return self.fn(*args, **kwargs)

        class SentenceHandlerFactory:
            # run check function out of order.
            # will finally transform the sentence to the form above
            # whatever _do function run, it must make the status dict look like this
            # status = {FN_object line[n], tuple connection[n], int toward_only[n], int backward_only[n]}
            def __init__(self, present_sentence_list, sentence_index, status):
                self.sentence = present_sentence_list[sentence_index]
                self.sentence_index = sentence_index
                self.present_sentence_list = present_sentence_list
                self.result = ""
                self.status = status
                for element in dir(self):
                    if element.startswith("_do"):
                        fn = getattr(self, element)
                        fn()
                self._translate()

            def _do_check_at_first_sentence(self):
                if self.sentence.startswith("THEN"):
                    self.result = self.sentence[5:]
                    self.status["connection"].append((self.sentence_index - 1, self.sentence_index))
                elif self.sentence.startswith("STARTL"):
                    self.result = ""
                else:
                    self.result = self.sentence
                    self.status["connection"].append((self.sentence_index - 1, self.sentence_index))

            def _do_check_if_sentence(self):
                if "condition" not in self.status.keys():
                    self.status["condition"] = []
                logging.info("handle %s when condition is %s" %(self.result, self.status["condition"]))
                if self.sentence.startswith("IF"):
                    self.status["condition"] += [[self.sentence_index]]
                    # self.status["connection"].append((self.sentence_index - 1, self.sentence_index))
                    self.result = self.sentence[3:]
                elif self.sentence.startswith("ELSE IF"):
                    if not self.status["condition"]:
                        raise Exception
                    self.status['connection'].append((self.status["condition"][-1][-1], self.sentence_index))
                    self.status["condition"][-1].append(self.sentence_index)
                    self.status["toward_only"].append(self.sentence_index)
                    self.result = self.sentence[8:]
                elif self.sentence.startswith("ELSE"):
                    self.status['connection'].append((self.status["condition"][-1][-1], self.sentence_index))
                    self.status["toward_only"].append(self.sentence_index)
                    self.result = self.sentence[5:]
                elif self.sentence.startswith("ENDIF"):
                    self.status["connection"].append((self.status["condition"][-1][-1], self.sentence_index))
                    self.status['condition'].pop(-1)
                    self.result = ''

            def _translate(self):
                loop = asyncio.get_event_loop()
                if not self.result:
                    self.status["line"].append(FN(loop.dictionary["None"], (), ()))
                    return

                single_word = self.result.split(' ')
                finding_attr = []
                return_attr = ""
                order_sentence = ''
                for item in single_word:
                    # what if ''
                    if item == '':
                        continue
                    if item[0] == '*':
                        finding_attr.append(item[1:])
                        order_sentence = order_sentence + '* '
                    elif item[0] == "&":
                        return_attr = item[1:]
                        order_sentence = order_sentence + '& '
                    else:
                        order_sentence = order_sentence + item + ' '
                order_sentence = order_sentence.rstrip()
                if order_sentence not in loop.dictionary:
                    logging.warning("%s cannot be translated" % self.result)
                    raise ValueError('the sentence \'%s\' cannot be translated ' % self.result)
                fn = loop.dictionary[order_sentence]
                rs = FN(fn, finding_attr, return_attr)
                logging.debug("when running %s, return is %s, args is %s, function is %s" %
                              (self.sentence, return_attr, finding_attr, fn.__name__))
                self.status["result"].add(return_attr)
                self.status["args"].update(finding_attr)
                self.status["line"].append(rs)

            def make_connection(self):
                conn = self.status["connection"]
                logging.debug("connection list %s ready to pair" % conn)
                line = self.status["line"]
                to = self.status["toward_only"]
                back = self.status["backward_only"]
                for t, b in conn:
                    # warning
                    if t in back:
                        back.remove(t)
                        logging.debug("the connection (%s, %s) not making connection" % (t, b))
                        continue
                    if b in to:
                        to.remove(b)
                        logging.debug("the connection (%s, %s) not making connection" % (t, b))
                        continue
                    logging.info("make connection between %s and %s when handling %s" % (t, b, line[t].fn.__name__))
                    line[t].set_later(b)

        if name == 'Order':
            return type.__new__(cls, name, bases, attrs)

        instruction = attrs['instruction']
        sentence_list = instruction.split("\n")
        status = {"connection": [], "toward_only": [], "backward_only": [], "line": [], "result": set(), "args": set()}
        sentence_list.append("STARTL")
        for index in range(len(sentence_list)):
            s = SentenceHandlerFactory(sentence_list, index, status)
        s.make_connection()
        attrs['line'] = status["line"]
        attrs['args'] = status["args"]
        attrs['results'] = status["result"]
        attrs['input_args'] = attrs['args'] - attrs['results']
        return type.__new__(cls, name, bases, attrs)


class Order(metaclass=NumberVectorMetaclass):
    def __init__(self, **kwargs):
        super().__init__()
        self.input_args = kwargs
        self.other_option = []
        self.present_index = -1
        self.args_dict = self.input_args
        self.exception = []
        loop = asyncio.get_event_loop()
        loop.create_task(self._run())

    async def _run(self):
        while True:
            try:
                coro = self.next_line()
            except StopIteration:
                return
            except Exception as e:
                raise e
            try:
                r = await coro
                if r:
                    if getattr(r, "__name__", None) == 'ConditionWrongException':
                        p = self.present_index
                        self.present_index = self.other_option[-1]
                        if p == self.present_index:
                            self.line[self.present_index].delete_later()
                        continue
                self.set_result_to_present_line(r)

            except BaseException as e:
                raise e
                self.set_exception_to_present_line(e)

    def next_line(self):
        while True:
            fn = self.line[self.present_index]
            try:
                index = fn.later_id[0]
                fn.delete_later()
                next_fn = self.line[index]
                self.present_index = index
                if len(next_fn.later_id) > 1:
                    self.other_option.append(self.present_index)
                l = []
                try:
                    for i in next_fn.inputer:
                        l.append(self.args_dict[i])
                except KeyError:
                    raise KeyError("check your code and fond out why a later called thing be used in advance "
                                   "%s not in %s" % (i, self.args_dict))
                return next_fn(*l)

            except IndexError:
                if self.present_index == len(self.line) -2:
                    raise StopIteration
                try:
                    self.present_index = self.other_option[-1]
                    return self.next_line()
                except IndexError:
                    if set(self.exception) - {ConditionWrongException}:
                        raise OrderFailedException
                    else:
                        raise StopIteration

    def set_result_to_present_line(self, result):
        r = self.line[self.present_index].results
        self.args_dict[r] = result

    def set_exception_to_present_line(self, e):

        self.exception.append(e)
