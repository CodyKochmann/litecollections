#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
from unittest import TestCase, main
from random import getrandbits, randint

from hypothesis import given
from hypothesis.strategies import text, integers

from litecollections import LiteSet

''' Main unittests for litecollections.LiteSet '''

def random_bytes():
    return getrandbits(128).to_bytes(16, 'little')

class Test_LiteSet(TestCase):
    ''' Main unittests for litecollections.LiteSet '''
    def test_all_methods_are_implemented(self):
        '''tests if all methods sets have are defined in LiteSet'''
        set_to_mirror = set()
        methods_of_a_set = {i for i in dir(set_to_mirror) if callable(getattr(set_to_mirror, i))}
        with LiteSet() as s:
            methods_of_a_LiteSet = {i for i in dir(s) if callable(getattr(s, i)) and i in methods_of_a_set}
            self.assertSetEqual(methods_of_a_set, methods_of_a_LiteSet)
        
    def test_int_members(self):
        '''test if ints can be used as members'''
        with LiteSet() as s:
            for k in range(10):
                self.assertNotIn(k, s)
                self.assertEqual(k, len(s))
                s.add(k)
                self.assertIn(k, s)
                self.assertEqual(k+1, len(s))
            for i in s:
                self.assertIsInstance(i, int)

    def test_str_members(self):
        '''test if ints can be used as members'''
        with LiteSet() as s:
            for _k in range(10):
                k = str(_k)
                self.assertNotIn(k, s)
                self.assertEqual(_k, len(s))
                s.add(k)
                self.assertIn(k, s)
                self.assertEqual(_k+1, len(s))
            for i in s:
                self.assertIsInstance(i, str)

    def test_byte_members(self):
        '''test if ints can be used as members'''
        with LiteSet() as s:
            for _k in range(10):
                k = random_bytes()
                self.assertNotIn(k, s)
                self.assertEqual(_k, len(s))
                s.add(k)
                self.assertIn(k, s)
                self.assertEqual(_k+1, len(s))
            for i in s:
                self.assertIsInstance(i, bytes)
    
    def test_length(self):
        '''tests if LiteSet mirrors what a set would do for len()'''
        with LiteSet() as s:
            test_string = 'hello world'
            set_to_mirror = set()
            for nth, letter in enumerate(test_string):
                s.add(letter)
                self.assertIn(letter, s)
                set_to_mirror.add(letter)
                self.assertIn(letter, set_to_mirror)
                self.assertEqual(len(set_to_mirror), len(s))

    
    def test_clear(self):
        '''tests if LiteSet mirrors what a set would do for set.clear()'''
        with LiteSet() as s:
            test_string = 'hello world'
            set_to_mirror = set()
            for nth, letter in enumerate(test_string):
                s.add(letter)
                self.assertIn(letter, s)
                set_to_mirror.add(letter)
                self.assertIn(letter, set_to_mirror)
                self.assertEqual(len(set_to_mirror), len(s))
                s.clear()
                set_to_mirror.clear()
                self.assertEqual(len(set_to_mirror), len(s))
                self.assertEqual(len(s), 0)

    def test_remove(self):
        '''tests if LiteSet mirrors what a set would do for set.remove()'''
        with LiteSet() as s:
            test_string = 'hello world'
            set_to_mirror = set()
            for nth, letter in enumerate(test_string):
                set_to_mirror.add(letter)
                self.assertIn(letter, set_to_mirror)
                s.add(letter)
                self.assertIn(letter, s)
                self.assertEqual(len(set_to_mirror), len(s))
                set_to_mirror.remove(letter)
                s.remove(letter)
                self.assertEqual(len(set_to_mirror), len(s))
                # ensure both raise KeyErrors if you try to remove letter twice
                with self.assertRaises(KeyError):
                    set_to_mirror.remove(letter)
                with self.assertRaises(KeyError):
                    s.remove(letter)

    def test_issubset(self):
        '''tests if LiteSet mirrors what a set would do for set.issubset()'''
        with LiteSet() as s:
            set_to_follow = set()
            for n in range(10):
                self.assertEqual(len(s), len(set_to_follow))
                self.assertEqual(len(s), n)
                set_to_follow.add(n)
                self.assertIn(n, set_to_follow)
                self.assertTrue(s.issubset(set_to_follow))
                self.assertFalse(set_to_follow.issubset(s))
                s.add(n)
                self.assertIn(n, s)
                self.assertTrue(s.issubset(set_to_follow))
                self.assertTrue(set_to_follow.issubset(s))

    def test_issuperset(self):
        '''tests if LiteSet mirrors what a set would do for set.issuperset()'''
        with LiteSet() as s:
            set_to_lead = set()
            for n in range(10):
                self.assertEqual(len(s), len(set_to_lead))
                self.assertEqual(len(s), n)
                s.add(n)
                self.assertIn(n, s)
                self.assertTrue(s.issuperset(set_to_lead))
                self.assertFalse(set_to_lead.issuperset(s))
                set_to_lead.add(n)
                self.assertIn(n, set_to_lead)
                self.assertTrue(s.issuperset(set_to_lead))
                self.assertTrue(set_to_lead.issuperset(s))

    def test_union(self):
        '''tests if LiteSet mirrors what a set would do for set.union against other LiteSets'''
        with LiteSet(range(0, 10)) as s1, LiteSet(range(10, 20)) as s2:
            s3 = s1.union(s2)
            self.assertIsInstance(s3, LiteSet)
            self.assertTrue(s1.issubset(s3))
            self.assertTrue(s2.issubset(s3))
            self.assertTrue(s3.issuperset(s1))
            self.assertTrue(s3.issuperset(s2))
            for i in s1:
                self.assertIn(i, s3)
            for i in s2:
                self.assertIn(i, s3)
    
    def test_union_against_set(self):
        '''tests if LiteSet mirrors what a set would do for set.union against other sets'''
        with LiteSet(range(0, 10)) as s1:
            s2 = set(range(10, 20))
            s3 = s1.union(s2)
            s4 = s2.union(s1)
            self.assertIsInstance(s3, LiteSet)
            self.assertIsInstance(s4, set)
            # test subsets against the LiteSet
            self.assertTrue(s1.issubset(s3))
            self.assertTrue(s2.issubset(s3))
            self.assertTrue(s3.issuperset(s1))
            self.assertTrue(s3.issuperset(s2))
            # ensure the same logic works with normal sets
            self.assertTrue(s1.issubset(s4))
            self.assertTrue(s2.issubset(s4))
            self.assertTrue(s4.issuperset(s1))
            self.assertTrue(s4.issuperset(s2))
            for i in s1:
                self.assertIn(i, s3)
                self.assertIn(i, s4)
            for i in s2:
                self.assertIn(i, s3)
                self.assertIn(i, s4)

    def test_difference(self):
        '''tests if LiteSet mirrors what a set would do for set.difference against other sets'''
        with LiteSet(range(0, 10)) as s1, LiteSet(range(5, 15)) as s2:
            std_s2 = set(range(5,15))
            self.assertSetEqual(s2, std_s2)
            self.assertSetEqual(
                s2.difference(s1),
                std_s2.difference(s1)
            )
            self.assertSetEqual(
                std_s2.difference(s1, s2),
                set()
            )
            self.assertSetEqual(
                s2.difference(s1, s2),
                set()
            )
            self.assertSetEqual(
                s1.difference(s2),
                s1.difference(std_s2)
            )

    def test_intersection(self):
        '''tests if LiteSet mirrors what a set would do for set.isdisjoint against other sets'''
        for _ in range(4):
            with LiteSet() as s1, LiteSet() as s2:
                for _ in range(4):
                    s1.add(randint(0, 8))
                    s2.add(randint(0, 8))
                std_s2 = set(s2)
                self.assertSetEqual(s2, std_s2)
                self.assertSetEqual(s2.intersection(s1), std_s2.intersection(s1))

    def test_isdisjoint(self):
        '''tests if LiteSet mirrors what a set would do for set.isdisjoint against other sets'''
        for _ in range(4):
            with LiteSet() as s1, LiteSet() as s2:
                for _ in range(4):
                    s1.add(randint(0, 8))
                    s2.add(randint(0, 8))
                std_s2 = set(s2)
                self.assertSetEqual(s2, std_s2)
                self.assertEqual(s2.isdisjoint(s1), std_s2.isdisjoint(s1), msg=f'{locals()}')

    def test_symmetric_difference(self):
        '''tests if LiteSet mirrors what a set would do for set.symmetric_difference against other sets'''
        for _ in range(4):
            with LiteSet() as s1, LiteSet() as s2:
                for _ in range(4):
                    s1.add(randint(0, 8))
                    s2.add(randint(0, 8))
                std_s2 = set(s2)
                self.assertSetEqual(s2, std_s2)
                self.assertSetEqual(s2.symmetric_difference(s1), std_s2.symmetric_difference(s1))

    def test_copy(self):
        '''tests if LiteSet mirrors what a set would do for set.copy'''
        for _ in range(4):
            with LiteSet() as s1:
                for _ in range(4):
                    s1.add(randint(0, 8))
                std_s1 = set(s1)
                s2 = s1.copy()
                std_s2 = std_s1.copy()
                self.assertSetEqual(s2, std_s2)
                item_to_remove = s1.pop()
                self.assertIn(item_to_remove, std_s1)
                self.assertIn(item_to_remove, s2)
                self.assertIn(item_to_remove, std_s2)
                s2.remove(item_to_remove)
                self.assertTrue(item_to_remove not in s2, msg='{locals()}')
                self.assertTrue(item_to_remove in std_s2, msg='{locals()}')
                std_s2.remove(item_to_remove)
                self.assertTrue(item_to_remove not in std_s2, msg='{locals()}')                
                self.assertSetEqual(s1, s2)
                self.assertSetEqual(s2, std_s2)
                s2.close()

    def test_difference_update(self):
        '''tests if LiteSet mirrors what a set would do for set.difference_update against other sets'''
        for _ in range(4):
            with LiteSet() as s1, LiteSet() as s2:
                for _ in range(4):
                    s1.add(randint(0, 8))
                    s2.add(randint(0, 8))
                std_s1 = set(s1)
                self.assertSetEqual(s1, std_s1)
                s1.difference_update(s2)
                std_s1.difference_update(s2)
                self.assertSetEqual(s1, std_s1)
                for i in s2:
                    self.assertNotIn(i, s1)
                    self.assertNotIn(i, std_s1)

class Test_LiteSet_HypthesisBeatdown(TestCase):
    def generate_type_test(self, member_strategy):
        '''acts as a harness for type hypothesis to try different type combos'''
        assert callable(member_strategy), member_strategy

        @given(member_strategy())
        def test(k):
            with LiteSet() as s:
                s.add(k)
                self.assertIn(k, s)
                # check if deduplication works
                len_before = len(s)
                s.add(k)
                self.assertEqual(len_before, len(s))
                # test deletion 
                s.discard(k)
                self.assertNotIn(k, s)
                # reinsert to keep building up a db
                s.add(k)
                self.assertIn(k, s)
        return test

    def test_str_keys_and_str_values(self):
        '''tests if hypothesis can come up with string members that LiteSet wont work with'''
        self.generate_type_test(text)()
    
    def test_str_keys_and_int_values(self):
        '''tests if hypothesis can come up with string members that LiteSet wont work with'''
        self.generate_type_test(integers)()

if __name__ == '__main__':
    main(verbosity=2)