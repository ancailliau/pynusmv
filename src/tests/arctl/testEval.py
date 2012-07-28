import unittest

from pynusmv.fsm.fsm import BddFsm
from pynusmv.dd.bdd import BDD
from pynusmv.init.init import init_nusmv, deinit_nusmv

from tools.arctl.parsing import parseArctl
from tools.arctl.ast import (Atom, Not, And, Or, Implies, Iff,
                             EaX, EaG, EaF, EaU, EaW,
                             AaX, AaG, AaF, AaU, AaW)
from tools.arctl.eval import evalArctl, evalArctl_from_string as evalStr


class TestEval(unittest.TestCase):
    
    def setUp(self):
        init_nusmv()
    
    def tearDown(self):
        deinit_nusmv()
    
    
    def init_model(self):
        fsm = BddFsm.from_filename("tests/arctl/model.smv")
        self.assertIsNotNone(fsm)
        return fsm
        
    
    def init_finite_model(self):
        fsm = BddFsm.from_filename("tests/arctl/finite_model.smv")
        self.assertIsNotNone(fsm)
        return fsm
        
        
    # FIXME There is a segfault when deinit_nusmv is called
    # if bdd is not deleted
    def test_atom(self):
        fsm = self.init_model()
        
        specs = parseArctl("'c'")
        self.assertEqual(len(specs), 1)
        spec = specs[0]
        self.assertEqual(type(spec), Atom)
        self.assertEqual(spec.value, "c")
        
        c = evalArctl(fsm, spec)
        self.assertIsNotNone(c)
        self.assertTrue(fsm.init <= c)
        del c
        
        
    def test_not(self):
        fsm = self.init_model()
        
        specs = parseArctl("~'c'")
        self.assertEqual(len(specs), 1)
        spec = specs[0]
        
        nc = evalArctl(fsm, spec)
        self.assertTrue((nc & fsm.init).is_false())
        
        del nc
        
        
    def test_and(self):
        fsm = self.init_model()
        
        candi = evalStr(fsm, "('c' & 'i')")
        c = evalStr(fsm, "'c'")
        i = evalStr(fsm, "'i'")
        self.assertEqual(candi, c & i)
        
        del candi, c, i
        
        
    def test_or(self):
        fsm = self.init_model()
        
        cordi = evalStr(fsm, "('c' | 'i')")
        c = evalStr(fsm, "'c'")
        i = evalStr(fsm, "'i'")
        self.assertEqual(cordi, c | i)
        
        del cordi, c, i
        
        
    def test_implies(self):
        fsm = self.init_model()
        
        cimpli = evalStr(fsm, "('c' -> 'i')")
        c = evalStr(fsm, "'c'")
        i = evalStr(fsm, "'i'")
        self.assertTrue(~c <= cimpli)
        self.assertTrue(i <= cimpli)
        self.assertEqual(~c | i, cimpli)
        
        del cimpli, c, i
        
        
    def test_iff(self):
        fsm = self.init_model()
        
        ciffi = evalStr(fsm, "('c' <-> 'i')")
        c = evalStr(fsm, "'c'")
        i = evalStr(fsm, "'i'")
        self.assertTrue(c & i <= ciffi)
        self.assertTrue(~c & ~i <= ciffi)
        self.assertEqual((c & i) | (~c & ~i), ciffi)
        
        del ciffi, c, i
        
        
    def test_eax(self):
        fsm = self.init_model()
        
        eaaxi = evalStr(fsm, "E<'a'>X 'i'")
        self.assertTrue((fsm.init & eaaxi).is_false())
        eaaxnc = evalStr(fsm, "E<'a'>X ~'c'")
        c = evalStr(fsm, "'c'")
        i = evalStr(fsm, "'i'")
        self.assertTrue(eaaxnc.isnot_false())
        self.assertEqual(eaaxnc, c.iff(i))
        del eaaxi, eaaxnc, c, i
        
    
    def test_neaxt(self):
        fsm = self.init_finite_model()
        
        candi = evalStr(fsm, "('c' & ~'i')")
        neaxt = evalStr(fsm, "~E<'a'>X 'TRUE'")
        
        self.assertTrue(candi <= neaxt)
        
        del candi, neaxt
        
        
    def test_aax(self):
        fsm = self.init_model()
        aaxnc = evalStr(fsm, "A<'a'>X ~'c'")
        c = evalStr(fsm, "'c'")
        i = evalStr(fsm, "'i'")
        self.assertEqual(aaxnc, c.iff(i))
        
        del aaxnc, c, i
    
      
    def test_aax_finite(self):
        fsm = self.init_finite_model()
        aaxnc = evalStr(fsm, "A<'a'>X ~'c'")
        c = evalStr(fsm, "'c'")
        i = evalStr(fsm, "'i'")
        self.assertEqual(fsm.init, aaxnc)
        self.assertEqual(aaxnc, c & i)
        
        del aaxnc, c, i
        
    
    def test_eaf(self):
        fsm = self.init_model()
        eafnc = evalStr(fsm, "E<'a'>F ~'c'")
        c = evalStr(fsm, "'c'")
        i = evalStr(fsm, "'i'")
        self.assertEqual(eafnc, ~(c & ~i))
        
        del eafnc, c, i
        
        
    def test_eaf_finite(self):
        fsm = self.init_finite_model()
        eafnc = evalStr(fsm, "E<'a'>F ~'c'")
        c = evalStr(fsm, "'c'")
        i = evalStr(fsm, "'i'")
        self.assertTrue(c.iff(i) <= eafnc)
        
        del eafnc, c, i
      
  
    # FIXME AaF fails
    @unittest.skip
    def test_aaf(self):
        fsm = self.init_model()
        aafni = evalStr(fsm, "A<'a'>F ~'i'")
        c = evalStr(fsm, "'c'")
        i = evalStr(fsm, "'i'")
        true = BDD.true(fsm.bddEnc.DDmanager)
        try:
            self.assertEqual(aafni, true)
        finally:
            print('deleting')
            del aafni, c, i, true
            print('deleted')
            
    
    # FIXME AaF fails
    @unittest.skip    
    def test_aaf_finite(self):
        fsm = self.init_finite_model()
        aafni = evalStr(fsm, "A<'a'>F ~'i'")
        self.assertEqual(aafni, BDD.true(fsm.bddEnc.DDmanager))
        
        del aafni