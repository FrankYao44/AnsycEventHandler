import asyncio
import my_loop
import PandoraHub
from order import Order
import unittest


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

            MyOrder = type('o', (Order,), {'instruction': "test *sth."})
            # self.assertEqual(MyOrder.line, {(0,): loop.dictionary["test *"]})
            self.assertEqual(MyOrder.entropy, 1)
            self.assertEqual(MyOrder.input_args, set(["sth"]))
            o = MyOrder(sth=2)
            loop.run_forever()


    unittest.main(verbosity=2)