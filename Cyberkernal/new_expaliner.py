
'''
this is the core class of the whole project.
>>> order = Order(**kw)
    new order created,new Task created.
>>> loop = asyncio.get_event_loop()
>>> loop.run_forever()
'after some time'
    the order has been done
'''


class TupleVectorMetaclass(type):
    '''
    the order class should have an attr named
    instruction like this:
    'if you are good, save you in database;if you are bad, save yourself in database.
    calc how good you are now.print it to me.
    for those who good is too low, kill them'
    we will simply translate it into a list like this
    [[[keyword1,keyword2],[keyword3,keyword4]],keyword5,keyword6,(keyword7,)]
    then we will look up the dictionary,translate them like this
    {(0,0,0):fn1,(0,0,1):fn2,.......,(3,):fn5,(4,):fn6........,(-1):return_to_first}
    meanwhile a variety of args will be inputted as followed
    finally added kwargs like this:
        line = {(0,0,0):fn1,.......} (just look up)
        entropy = len(line.keys()[0])
        restriction = [FN, FN ]
        args = [*args]
        input_args = [*args] - [*result]
        results = [..]


    '''
    def __new__(mcs, name, bases, attrs):
        def explainer(sentence):
            def position(var, present_position=0, condition=False):
                if not getattr(var, 'postion', None):
                    var.position = [present_position]
                    return
                if condition:
                    var.position.append(0)
                else:
                    var.position[-1] += 1

            def normal_sentence(n_sentence, present_position=0, condition=False):

                if n_sentence.find(',') + 1:
                    single_order = n_sentence.split(',')
                    result = []
                    for k in range(len(single_order)):
                        result.append(normal_sentence(single_order[k], k))
                    return result
                single_word = n_sentence.split(' ')
                finding_attr = []
                order_sentence = ''
                for item in single_word:
                    # what if ''
                    if item == '':
                        continue
                    if item[0] == '*':
                        finding_attr.append(item[1:])
                        order_sentence = order_sentence + '* '
                    else:
                        order_sentence = order_sentence + item + ' '
                order_sentence = order_sentence.rstrip()
                loop = asyncio.get_event_loop()
                if order_sentence not in loop.dictionary:
                    print(loop.dictionary)
                    raise ValueError('the sentence \'%s\' cannot be translated ' % n_sentence)
                fn = loop.dictionary[order_sentence]
                fn.really_input = finding_attr
                position(fn, present_position, condition)
#               if set(fn.params) != set(finding_attr):
#                   raise ValueError('takes argument %s, but %s was given' % (fn.params, finding_attr))
                return fn

            def condition_sentence(c_sentence):
                # double condition is not allowed
                the_rest = c_sentence
                result = []
                the_if = []
                the_next = 'if'
                while True:
                    m = the_rest.find('if ')
                    n = the_rest.find('then ')
                    if n == m == -1:
                        break
                    if (m < n) & (m != -1):
                        if the_next == 'then':
                            raise ValueError('sentence %s error. check if you use double \'if\' ' % c_sentence)
                        s = the_rest[3:n]
                        the_if = normal_sentence(s)
                        the_rest = the_rest[n:]
                        the_next = 'then'
                    if (n < m) | (m == -1):
                        if n == -1:
                            raise ValueError('sentence %s error. check if you use single \'if\' ' % c_sentence)
                        if the_next == 'if':
                            raise ValueError('sentence %s error. check if you use double \'then\' ' % c_sentence)
                        s = the_rest[5:m]
                        the_then = explainer(s)
                        the_rest = the_rest[m:]
                        result += [the_if, the_then]
                return result

            def restriction_sentence(r_sentence):
                # for those who
                result = r_sentence[14:]
                m = result.split(',then ')
                result = map(normal_sentence, m)
                return result
            if sentence.find('if')+1:
                return condition_sentence(sentence)
            elif sentence.find('for those who')+1:

                return tuple(['r', restriction_sentence(sentence)])
            else:

                return normal_sentence(sentence)

        if name == 'Order':
            return type.__new__(mcs, name, bases, attrs)
        '''
        won't be edited until I learn NN
        now it will be created by user
        aimed to translate args in Order child class into order_line
        '''
        # here to explain words
        string = attrs['instruction']
        line = {}
        restriction = []
        entropy = 1
        explained_line = []
        args = set()
        results = set()
        instruction_list = string.split('.')
        if instruction_list[-1] == "":
            instruction_list.pop()
        explained_line += list(map(explainer, instruction_list))
        for i in explained_line:
            if isinstance(i, tuple):
                if i[0] == 'rs':
                    restriction += i
                    explained_line.remove(i)
        present_id_list = []
        line = {}
        present_index = 0

        def position_judgement(order_list):
            for i in order_list:
                if callable(i):
                    line[present_index] = i
                    if not present_id_list:
                        line[present_id_list[-1]].towards.append(present_index)
                    else:
                        present_id_list.append(present_index)
                    present_index += 1

                else:
                    position_judgement(i)

        k = 0
        position_judgement(explained_line, i.index)

        for i in line.keys():
            if len(i) >= entropy:
                entropy = len(i)
        for i in line.keys():
            rs = i
            while len(i) < entropy:
                rs += (0,)
            line[rs] = line[i]
            if i != rs:
                line.pop(i)
            if getattr(line[rs], 'vector', None):
                while len(line[rs].vector) < entropy:
                    line[rs].vector += [0]
                line[rs].vector = array(line[rs].vector)
        for i in line.values():
            args.update(set(i.input))
            results.update(set(i.results))
        loop = asyncio.get_event_loop()
        a = [0 for _ in range(entropy)]
        a[0] = 1
        b = [0 for _ in range(entropy)]
        b[0] = -1
        line[tuple(b)] = loop.dictionary["start"]
        line[tuple(b)].vector = [array(a)]
        input_args = set()
        [input_args.update(v.really_input) for v in line.values() if callable(v)]
        attrs['line'] = line
        attrs['entropy'] = entropy
        attrs['restriction'] = restriction
        attrs['args'] = args
        attrs['input_args'] = tuple(input_args)
        attrs['results'] = results
        #print('start  ',string,'\n',line,'\n',restriction,'\n',entropy,'\n',explained_line,'\n',input_args,'\n',results,'\n',instruction_list,'\n',' end')
        return type.__new__(mcs, name, bases, attrs)


class OldOrder(dict, metaclass=TupleVectorMetaclass):
    """
        the metaclass must have done these:
        it has created a list like this
        [(1,2,2,1,3,3)=fn1,(1,3,4,2)=fn2)]
        which key is used as identification
        fn which has some additional args , such as params, next_id, really_input
        meanwhile some list will be inputted
        restriction, args_name(all the args will be posted),
        input_args_name(those you must input in advance), results_name(the result of fn)
    """

    # self.line ,inherited from list, is simply a list
    def __init__(self, **kwargs):
        super().__init__()
        self.update(self.line)
#        if set(kwargs.keys()) != self.input_args:
#            raise ValueError('takes %s positional argument but %s were given' % (self.input_args, list(kwargs.keys())))
        self.input_args = kwargs
        self.other_option = {}
        self.have_run_position = ()
        self.have_run_result = dict()
        self.exception = []
        a = [0 for _ in range(self.entropy)]
        a[0] = -1
        self.present_position = tuple(a)
        self.next_position_vector = ()
        loop = asyncio.get_event_loop()
        loop.create_task(self._run())

    async def _run(self):
        while True:
            try:
                coro = self.next_line()
            except StopIteration:
                break
            try:
                r = await coro
                self.set_result_to_present_line(r)
            except BaseException as e:
                self.set_exception_to_present_line(e)

    def next_line(self):
        # use id to judge which way to continue
        if not getattr(self.line[self.present_position], 'vector', None):
            raise StopIteration
        if len(self.line[self.present_position].vector) != 1:
            if self.present_position not in self.other_option.keys():
                self.other_option[self.present_position] = self.line[self.present_position].vector
            while list(self.other_option.keys())[-1] is []:
                self.other_option.pop(list(self.other_option.keys())[-1])
                try:
                    self.present_position = list(self.other_option.keys())[-1]
                except IndexError:
                    raise OrderFailedException(self.exception)
            vector = self.other_option[self.present_position][0]
            self.other_option[self.present_position].pop(0)
            v = array(self.present_position) + vector
            self.present_position = tuple(v.tolist()[0])
        else:
            self.present_position = tuple((array(self.present_position)
                                           + self.line[self.present_position].vector).tolist()[0])
        fn = self.line[self.present_position]
        args = []
        for i, j in self.have_run_result.items():
            if i in fn.really_input:
                args.append(j)
        for i, j in self.input_args.items():
            if i in fn.really_input:
                args.append(j)

        return fn(*args)

    def set_result_to_present_line(self, result):
        r = self.line[self.present_position].results
        for i in range(len(r)):
            self.have_run_result[r(i)] = result[i]

    def set_exception_to_present_line(self, e):

        self.exception.append(e)
