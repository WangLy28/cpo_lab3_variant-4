import unittest
# from mfsm import*
from mfsm import DiscreteEvent, Node, source_event


import graphviz


class DiscreteEventTest(unittest.TestCase):

    def test_elevator(self):
        m = DiscreteEvent("elevator")
        m.input_port("Overload", latency=1)
        m.input_port("Go_Up", latency=1)
        m.output_port("Going_Up", latency=1)
        m.output_port("Going_Down", latency=1)
        m.output_port("Halt", latency=1)

        def add_load(a, b):
            n = m.add_node(
                "{}".format(b), lambda a: not a if isinstance(a, bool)
                else None)
            n.input(a, 1)
            n.output(b, 1)

        def add_convert(a, b, c):
            n = m.add_node("{} and {}".format(a, b),
                           lambda a, b: a and b
                           if isinstance(a, bool) and isinstance(b, bool)
                           else None)
            n.input(a, 1)
            n.input(b, 1)
            n.output(c, 1)

        add_load("Overload", "Not_Overload")
        add_load("Go_Up", "Go_Down")

        add_convert("Not_Overload", "Go_Up", "Going_Up")
        add_convert("Not_Overload", "Go_Down", "Going_Down")
        add_convert("Overload", "Go_Up", "Halt")
        add_convert("Overload", "Go_Down", "Halt")

        test_data = [
            ({'Overload': True, 'Go_Up': None},
             {'Going_Up': None, 'Going_Down': None, 'Halt': None}),
        ]
        for a, d in test_data:
            source_events = [source_event(k, v, 0) for k, v in a.items()]
            actual = m.execute(*source_events)
            expect = {}
            expect.update(actual)
            expect.update(d)
            # self.assertEqual(actual, expect)
        # print(m.visualize())
        dot = m.visualize()
        f = open('fsm.dot', 'w')
        f.write(dot)
        f.close()

        with open("fsm.dot") as f:
            dot_graph = f.read()
        dot = graphviz.Source(dot_graph)
        dot.view()

    # Node test
    def test_convert_self_state(self):
        n = Node("convert_self_state",
                 lambda x: not x if isinstance(x, bool) else None)
        n.input("A", 1)
        n.output("B", 1)
        test_data = [
            (False, True),
            (False, True),
            (None, None),
        ]
        for a, b in test_data:
            self.assertEqual(n.activate({"A": a}), [source_event("B", b, 1)])

    def test_add_convert(self):
        n = Node("convert",
                 lambda x, y: x and y
                 if isinstance(x, bool) and isinstance(y, bool) else None)
        n.input("A", 1)
        n.input("B", 1)
        n.output("C", 1)
        test_data = [
            (None, False, None),
            (False, False, False),
            (True, False, False),
            (False, True, False),
            (True, True, True),
        ]
        for a, b, c in test_data:
            self.assertEqual(n.activate({"A": a, "B": b}),
                             [source_event("C", c, 1)])

    def test_convert(self):
        def convert(x):
            if x == 0:
                return 0, 1
            if x == 1:
                return 1, 0
            return None, None

        n = Node("convert", convert)
        n.input("A", 1)
        n.output("D1", 1)
        n.output("D0", 2)
        test_data = [
            (0, 0, 1),
            (1, 1, 0),
            (None, None, None),
        ]
        for a, d1, d0 in test_data:
            self.assertEqual(n.activate({"A": a}),
                             [source_event("D1", d1, 1),
                              source_event("D0", d0, 2)])


if __name__ == '__main__':
    unittest.main()
