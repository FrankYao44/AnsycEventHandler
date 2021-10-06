import asyncio
from Cyberkernal import my_loop
import PandoraHub
from Cyberkernal.order import Order
import unittest
import warnings
warnings.simplefilter("ignore")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    async def a():
        return 0

    asyncio.run(a())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    class Test(unittest.TestCase):
        def test_0_check_dictionary(self):
            self.assertIn('network for * init',loop.dictionary)
            self.assertIn('network for * close', loop.dictionary)
            self.assertIn('just get from *', loop.dictionary)
            self.assertIn('just run in process * of * with *', loop.dictionary)
            self.assertIn('just run in threading * of * with *', loop.dictionary)
            self.assertIn('just run in network * of * with *', loop.dictionary)
            self.assertIn('just findall * in * of * by *', loop.dictionary)
            self.assertIn('test *', loop.dictionary)

        def test_1_at_least_runnable(self):

            MyOrder = type('o', (Order,), {'instruction': "test *sth"})
            self.assertEqual([a.fn for a in MyOrder.line], [loop.dictionary["test *"], loop.dictionary["None"]])
            self.assertEqual(MyOrder.input_args, {"sth"})
            self.assertEqual([a.later_id for a in MyOrder.line], [[], [0]])
            o = MyOrder(sth=2)

        def test_2_run_condition(self):

            MyOrder = type('o', (Order,), {'instruction': "test *sth\n"
                                                          "IF i am right\n"
                                                          "i am right\n"
                                                          "THEN test *another_thing\n"
                                                          "IF i am wrong\n"
                                                          "i am right\n"
                                                          "THEN test *sth\n"
                                                          "ENDIF\n"
                                                          "ENDIF"

                                           })
            self.assertEqual(MyOrder.input_args, {"sth", "another_thing"})
            self.assertEqual([a.later_id for a in MyOrder.line], [[1], [2, 8], [3], [4], [5, 7], [6], [7], [8], [], [0]])
            o = MyOrder(sth=8, another_thing=0)

        def test_2_run_condition2(self):

            MyOrder = type('o', (Order,), {'instruction': "test *sth\n"
                                                          "IF i am right\n"
                                                          "i am wrong\n"
                                                          "THEN test *another_thing\n"
                                                          "IF i am wrong\n"
                                                          "THEN test *sth\n"
                                                          "ELSE IF i am right\n"
                                                          "THEN test *sth to &another\n"
                                                          "test *another\n"
                                                          "ENDIF\n"
                                                          "ELSE test *sth to &another\n"
                                                          "test *another\n"
                                                          "ENDIF"


                                           })
            self.assertEqual(MyOrder.input_args, {"sth", "another_thing"})
            # self.assertEqual([a.later_id for a in MyOrder.line], [[1], [2, 10], [3], [4], [5, 6], [], [7, 9], [8], [9], [10], [], [0]])
            o = MyOrder(sth=9, another_thing=0)


        def test_3_Process(self):
            MyOrder = type('o', (Order,), {'instruction': "process for *Expand init\n"
                                                          "just run in process *fn_name of *Expand with *kw to &a\n"
                                                          "test *a\n"
                                                            "process for *Expand all terminate"})
            #
                           #                               "process for *Expand all terminate"
            o = MyOrder(fn_name="calc", Expand="test", kw={"num": 2333})


        def test_4_Thread(self):
            MyOrder = type('o', (Order,), {'instruction': "thread for *exp init\n"
                                                          "just run in thread *fn of *exp with *kw to &a\n"
                                                          "test *a\n"
                                                          "thread for *exp all terminate"})
            MyOrder(fn="calc", exp="test", kw={"num": 338})

        def test_5_neteork(self):
            pass

        def test_6_database(self):
            pass

        def test_9_exception_catcher(self):
            loop.run_forever()


    unittest.main(verbosity=2)