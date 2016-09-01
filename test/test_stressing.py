from support import lib, ffi
from qcgc_test import QCGCTest
import random, time, unittest

class StressTestCase(QCGCTest):
    output = False

    def push_all_roots(self):
        # use before operations that may cause collections
        self.assertTrue(self.ss_size() == 0)
        for p in self.root_set:
            self.push_root(p)
        self.assertTrue(self.ss_size() == len(self.root_set))

    def pop_all_roots(self):
        # use after operations that may cause collections
        self.assertTrue(self.ss_size() == len(self.root_set))
        for _ in self.root_set:
            p = self.pop_root()
            self.assertTrue(p in self.root_set)
        self.assertTrue(self.ss_size() == 0)

    def allocate(self):
        # allocate a few objects
        self.push_all_roots()
        for _ in range(random.randint(0, 100)):
            nrefs = random.randint(1, 1000)

            new_obj = self.allocate_ref(nrefs)
            self.push_root(new_obj)

            # obj to all sets
            self.root_set.append(new_obj)
            self.shadow_root_set[new_obj] = [None] * nrefs
            self.shadow_objs[new_obj] = self.shadow_root_set[new_obj]

        self.pop_all_roots()

    def mutate(self):
        # mutate a few references
        for _ in range(random.randint(0, 100)):
            o1 = random.choice(self.root_set)
            o2 = random.choice(self.root_set)

            self.set_ref(o1, 0, o2)
            self.shadow_root_set[o1][0] = o2
            assert self.shadow_objs[o1][0] == o2
            assert self.get_ref(o1, 0) == o2

    def forget(self):
        # forget a few root objs
        num_roots = min(100, len(self.root_set))
        for _ in range(random.randint(0, num_roots - 1)):
            idx = random.randint(0, len(self.root_set) - 1)
            o = self.root_set[idx]
            del self.root_set[idx]
            del self.shadow_root_set[o]
            # not from self.shadow_objs yet, as they may survive indirectly


    def assert_valid_gc_object(self, obj):
        self.assertIn(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", obj)), [
                lib.BLOCK_BLACK, lib.BLOCK_WHITE ])

    def _collect_shadow_objs(self):
        found = set()
        todo = set(self.shadow_root_set.keys())
        while todo:
            o = todo.pop()
            if o is not None and o not in found:
                found.add(o)
                todo.add(self.shadow_objs[o][0])
        return found

    def _collect_real_objs(self):
        found = set()
        todo = set(self.root_set)
        while todo:
            o = todo.pop()
            if o != ffi.NULL and o not in found:
                found.add(o)
                todo.add(self.get_ref(o, 0))
        return found

    def dump_real_obj_graph(self):
        links = {}
        todo = set(self.root_set)
        while todo:
            o = todo.pop()
            if o != ffi.NULL and o not in links.keys():
                r = self.get_ref(o, 0)
                links[o] = r if r != ffi.NULL else None
                todo.add(r)
        self.to_dot('real.png', links)

    def dump_shadow_obj_graph(self):
        links = {}
        todo = set(self.shadow_root_set.keys())
        while todo:
            o = todo.pop()
            if o is not None and o not in links.keys():
                r = self.shadow_objs[o][0]
                links[o] = r
                todo.add(r)
        self.to_dot('shadow.png', links)

    def to_dot(self, filename, edges):
        from pygraphviz import AGraph
        dot = AGraph(directed=True)
        for n in edges.keys():
            dot.add_node(str(n))
            if lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", n)) not in [
                    lib.BLOCK_BLACK, lib.BLOCK_WHITE]:
                node = dot.get_node(str(n))
                node.attr['color'] = 'red'
        for n in edges.keys():
            if edges[n] is not None:
                dot.add_edge(str(n), str(edges[n]))
        dot.layout(prog='dot')
        dot.draw(filename)


    def check(self):
        # compare tracing through shadow_root_set and root_set
        for o in self.root_set:
            self.assert_valid_gc_object(o)
        for o in self.shadow_root_set.keys():
            self.assert_valid_gc_object(o)
        #
        self.assertEqual(len(self.root_set), len(self.shadow_root_set))
        self.assertSetEqual(set(self.root_set), set(self.shadow_root_set.keys()))
        #
        shadow_objs = self._collect_shadow_objs()
        real_objs = self._collect_real_objs()
        #
        for o in shadow_objs:
            self.assert_valid_gc_object(o)
        for o in real_objs:
            self.assert_valid_gc_object(o)
        #
        self.assertEqual(shadow_objs, real_objs)
        if self.output:
            print("objs alive: {}".format(len(real_objs)))

        # purge all non-found/reachable objs from shadow_objs
        for o in list(self.shadow_objs):
            if o not in shadow_objs:
                del self.shadow_objs[o]

    def test_stress(self):
        random.seed(42)

        # set of roots to push
        self.root_set = list()
        # shadow rootset for validation (obj => [ref]
        self.shadow_root_set = {}
        # all shadow objs (some may be dead)
        self.shadow_objs = {}

        for i in range(1000):
            self.allocate()
            self.mutate()
            self.forget()
            if i % 30 == 0:
                t = time.time()
                self.push_all_roots()
                lib.qcgc_collect()
                self.pop_all_roots()
                if self.output:
                    print("collect time: {}".format(time.time() - t))
            self.check()

if __name__ == "__main__":
    unittest.main()
