#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
from unittest import TestCase, main
from random import getrandbits

from hypothesis import given
from hypothesis.strategies import text, integers

from litecollections import LiteDict

''' Main unittests for litecollections.LiteDict '''

def random_bytes():
    return getrandbits(128).to_bytes(16, 'little')

class Test_LiteDict(TestCase):
    ''' Main unittests for litecollections.LiteDict '''
    def test_int_keys(self):
        '''test if ints can be used as keys'''
        with LiteDict() as d:
            for k in range(10):
                assert k not in d
                assert k == len(d), [k, len(d)]
                d[k] = 'waffle'
                assert k in d
                assert d[k] == 'waffle', repr(d[k])
                assert k+1 == len(d), [k+1, len(d)]

    def test_str_keys(self):
        '''test if strings can be used as keys'''
        with LiteDict() as d:
            for _k in range(10):
                k=str(_k)
                assert k not in d, [k, d.keys()]
                assert _k == len(d), [_k, len(d)]
                d[k] = 'waffle'
                assert k in d, [k, d.keys()]
                assert d[k] == 'waffle', repr(d[k])
                assert _k+1 == len(d), [_k+1, len(d)]

    def test_random_byte_keys(self):
        '''test if bytes can be used as keys'''
        with LiteDict() as d:
            for _k in range(10):
                k=random_bytes()
                assert k not in d, [k, d.keys()]
                assert _k == len(d), [_k, d]
                d[k] = 'waffle'
                assert k in d, [k, d.keys()]
                assert d[k] == 'waffle', repr(d[k])
                assert _k+1 == len(d), [_k+1, len(d)]
    
    def test_length_functionality(self):
        '''tests if LiteDict mirrors what a dict would do for len()'''
        with LiteDict() as d:
            test_string = 'hello world'
            dict_to_mirror = {}
            for nth, letter in enumerate(test_string):
                d[letter] = nth
                dict_to_mirror[letter] = nth
                self.assertEqual(len(dict_to_mirror), len(d))

    #def test_str_keys_with_persistence(self):
    #    print('now for persistence (this should fail if ran twice)')
    #    with LiteDict('persistent_dict.db') as d:
    #        for _k in range(10):
    #            k=str(_k)
    #            assert k not in d, [k, d.keys()]
    #            assert _k == len(d), [_k, d]
    #            d[k] = 'waffle'
    #            assert k in d, [k, d.keys()]
    #            assert d[k] == 'waffle', repr(d[k])
    #            assert _k+1 == len(d), [_k+1, len(d)]

class Test_LiteDict_HypthesisBeatdown(TestCase):
    def generate_type_combo_test(self, key_strategy, value_strategy):
        '''acts as a harness for type hypothesis to try different type combos'''
        assert callable(key_strategy), key_strategy
        assert callable(value_strategy), value_strategy

        @given(key_strategy(), value_strategy())
        def test(k, v):
            with LiteDict() as d:
                d[k] = v
                self.assertIn(k, d)
                self.assertEqual(d[k], v)
                try:
                    v + v # check if the values can be added together
                except:
                    pass
                else:
                    # if they can, update the key with the values added together and test if the value updated
                    d[k] = v + v
                    self.assertIn(k, d)
                    self.assertEqual(d[k], v + v)
                # test deletion 
                del d[k]
                self.assertNotIn(k, d)
                # reinsert to keep building up a db
                d[k] = v
                self.assertIn(k, d)
                self.assertEqual(d[k], v)
        return test

    def test_str_keys_and_str_values(self):
        '''tests if hypothesis can come up with string keys that LiteDict wont work with if using string values'''
        self.generate_type_combo_test(text, text)()
    
    def test_str_keys_and_int_values(self):
        '''tests if hypothesis can come up with string keys that LiteDict wont work with if using int values'''
        self.generate_type_combo_test(text, integers)()

if __name__ == '__main__':
    main(verbosity=2)