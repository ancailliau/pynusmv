import unittest

from pynusmv.init.init import init_nusmv, deinit_nusmv
from pynusmv.fsm.bddFsm import BddFsm
from pynusmv.dd.bdd import BDD
from pynusmv.mc.mc import eval_simple_expression as evalSexp
from pynusmv.utils.exception import NuSMVBddPickingError

class TestFsm(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
        
    def tearDown(self):
        deinit_nusmv()
        
    def model(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/constraints.smv")
        self.assertIsNotNone(fsm)
        return fsm
        
        
    def test_init(self):
        fsm = self.model()
        
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        
        self.assertEqual(p & q, fsm.init)
        
        
    def test_state_constraints(self):
        fsm = self.model()
        
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        
        self.assertEqual(p | q, fsm.state_constraints)
        
        
    def test_inputs_constraints(self):
        fsm = self.model()
        
        true = BDD.true(fsm.bddEnc.DDmanager)
        
        self.assertEqual(true, fsm.inputs_constraints)
        
        
    def test_pre(self): 
        fsm = self.model()
        
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        self.assertEqual(q, fsm.pre(~p & q))
        self.assertEqual(p & q, fsm.pre(~p & q, a))
        
        
    def test_post_counters(self):
        fsm = BddFsm.from_filename("tests/pynusmv/models/counters.smv")
        self.assertIsNotNone(fsm)
        
        c1c0 = evalSexp(fsm, "c1.c = 0")
        c1c1 = evalSexp(fsm, "c1.c = 1")
        c2c0 = evalSexp(fsm, "c2.c = 0")
        c2c1 = evalSexp(fsm, "c2.c = 1")
        rc1 = evalSexp(fsm, "run = rc1")
        rc2 = evalSexp(fsm, "run = rc2")
        
        self.assertEqual(fsm.post(c1c0 & c2c0), (c1c1 & c2c0) | (c1c0 & c2c1))
        
        
    def test_post(self): 
        fsm = self.model()
        
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        self.assertEqual(~p & q, fsm.post(~p & q))
        self.assertEqual(p & ~q, fsm.post(p & q, ~a))
        
        
    def test_pick_one_state(self):
        fsm = self.model()
        
        false = BDD.false(fsm.bddEnc.DDmanager)
        true = BDD.true(fsm.bddEnc.DDmanager)
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        s = fsm.pick_one_state(p)
        self.assertTrue(false < s < p < true)
        with self.assertRaises(NuSMVBddPickingError):
            s = fsm.pick_one_state(false)
        s = fsm.pick_one_state(true)
        self.assertTrue(s.isnot_false())
        self.assertTrue(false < s < p < true or false < s < ~p < true)
        self.assertTrue(false < s < q < true or false < s < ~q < true)
        
        
    def test_pick_one_state_error(self):
        fsm = self.model()
        
        false = BDD.false(fsm.bddEnc.DDmanager)
        true = BDD.true(fsm.bddEnc.DDmanager)
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        with self.assertRaises(NuSMVBddPickingError):
            s = fsm.pick_one_state(false)
            
        with self.assertRaises(NuSMVBddPickingError):
            s = fsm.pick_one_state(a)
        
        
        
    def test_pick_one_inputs(self):
        fsm = self.model()
        
        false = BDD.false(fsm.bddEnc.DDmanager)
        true = BDD.true(fsm.bddEnc.DDmanager)
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        ac = fsm.pick_one_inputs(a)
        self.assertTrue(false < ac <= a < true)
        self.assertTrue(ac == a)
        self.assertTrue(ac.isnot_false())
        ac = fsm.pick_one_inputs(true)
        self.assertTrue(false < ac < true)
        self.assertTrue(ac == a or ac == ~a)
        
        
    def test_pick_one_inputs_error(self):
        fsm = self.model()
        
        false = BDD.false(fsm.bddEnc.DDmanager)
        true = BDD.true(fsm.bddEnc.DDmanager)
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        with self.assertRaises(NuSMVBddPickingError):
            i = fsm.pick_one_inputs(false)
            
        with self.assertRaises(NuSMVBddPickingError):
            i = fsm.pick_one_inputs(p)
        
        
    def test_get_inputs(self):
        fsm = self.model()
        
        false = BDD.false(fsm.bddEnc.DDmanager)
        true = BDD.true(fsm.bddEnc.DDmanager)
        p = evalSexp(fsm, "p")
        q = evalSexp(fsm, "q")
        a = evalSexp(fsm, "a")
        
        ac = fsm.get_inputs_between_states(p & q, p & ~q)
        self.assertTrue(ac == ~a)
        ac = fsm.get_inputs_between_states(p, p)
        self.assertTrue(ac == true)
        
        self.assertTrue(q == (p & q) | (~p & q))
        self.assertTrue(q.iff(~p) == (~p & q) | (p & ~q))
        ac = fsm.get_inputs_between_states(q, q.iff(~p))
        self.assertTrue(ac == true)
        
        
    def test_get_trans(self):
        fsm = self.model()
        
        trans = fsm.trans
        self.assertIsNotNone(trans)
        
        bdd = trans.monolithic
        self.assertIsNotNone(bdd)
        
        
    def test_set_trans(self):
        fsm = self.model()
        
        trans = fsm.trans
        self.assertIsNotNone(trans)
        
        fsm.trans = trans