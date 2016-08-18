from support import lib, ffi
from qcgc_test import QCGCTest
import random, time, unittest

class StressTestCase(QCGCTest):

    def push_all_roots(self):
        # use before operations that may cause collections
        self.assertTrue(self.ss_size() == 0)
        for p in self.root_set:
            self.push_root(p)

    def pop_all_roots(self):
        # use after operations that may cause collections
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

    def forget(self):
        # forget a few root objs
        num_roots = min(100, len(self.root_set))
        for _ in range(random.randint(0, num_roots - 1)):
            idx = random.randint(0, len(self.root_set) - 1)
            o = self.root_set[idx]
            del self.root_set[idx]
            del self.shadow_root_set[o]
            # not from self.shadow_objs yet, as they may survive indirectly


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


    def check(self):
        # compare tracing through shadow_root_set and root_set
        self.assertEqual(len(self.root_set), len(self.shadow_root_set))
        shadow_objs = self._collect_shadow_objs()
        real_objs = self._collect_real_objs()
        self.assertEqual(shadow_objs, real_objs)
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

        for i in range(10000):
            self.allocate()
            self.mutate()
            self.forget()
            if i % 30 == 0:
                t = time.time()
                lib.qcgc_collect()
                print("collect time: {}".format(time.time() - t))
            self.check()

if __name__ == "__main__":
    unittest.main()
