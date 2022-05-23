#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import chain

from .LiteCollection import LiteCollection
from .LiteExceptions import InvalidPositionalArgCount, EmptyLiteSet
from .loader import load, dump



def hashable(obj) -> bool:
    ''' boolean check for hashable inputs '''
    try:
        hash(obj)
    except:
        return False
    else:
        return True

class LiteSet(LiteCollection):
    ''' python dict but backed by a sqlite database '''
    schema = [
        '''
            CREATE TABLE IF NOT EXISTS value_store(
                value TEXT UNIQUE ON CONFLICT IGNORE,
                CHECK(json_valid(value))
            )
        '''
    ]
    _default_db_path = LiteCollection._default_db_path
    
    def __init__(self, *set_args, db_path=_default_db_path):
        assert isinstance(set_args, tuple), set_args
        if len(set_args) not in {0, 1}:  # test for valid positional arg count
            raise InvalidPositionalArgCount(f'LiteSet only supports 1 positional arg which needs to be an iterable, got {len(set_args)}')
        assert isinstance(db_path, str), db_path
        # assemble the backend
        LiteCollection.__init__(
            self,
            LiteSet.schema,
            db_path=db_path
        )
        # load in any data passed to the constructor
        if set_args:
            # if other args exist, the user probably wants
            # the normal set() constructor behavior
            iter(set_args[0])  # assert set_args[0] is iterable
            self.update(set_args[0])
        
    def __contains__(self, value):
        assert hashable(value), f'unhashable input {value}'
        query = self._cursor.execute(
            '''
                SELECT count(value) FROM value_store WHERE value=? LIMIT 1
            ''',
            [dump(value)]
        )
        for count, in query:
            return count == 1
        assert False, 'this line should never happen'

    def add(self, value):
        '''adds new values to the LiteSet'''
        assert hashable(value), f'unhashable input {value}'
        list(self._cursor.execute(
            'insert into value_store(value) VALUES (?)',
            [dump(value)]
        ))
        if self._autocommit:
            self.commit()

    def clear(self):
        '''Remove all elements from this LiteSet'''
        list(self._cursor.execute(
            'delete from value_store'
        ))
        if self._autocommit:
            self.commit()

    def pop(self):
        '''Remove and return an arbitrary LiteSet element. Raises EmptyLiteSet(KeyError) if the set is empty.'''
        if len(self) == 0:
            raise EmptyLiteSet('pop from an empty set')
        return_value = None
        for i in self:
            return_value = i
            break
        self.discard(return_value)
        return return_value

    def discard(self, value):
        '''Remove an element from the LiteSet if it is a member. If the element is not a member, do nothing.'''
        assert hashable(value), f'unhashable input {value}'
        list(self._cursor.execute(
            'delete from value_store where value=?',
            [dump(value)]
        ))
        if self._autocommit:
            self.commit()
    
    def remove(self, value):
        '''Remove an element from a set; it must be a member. If the element is not a member, raise a KeyError.'''
        if value in self:
            self.discard(value)
        else:
            raise KeyError(value)
    
    def issubset(self, another_set):
        '''Report whether another set contains this set'''
        # see if we can short cut with len() alone
        l = len(self)
        if l == 0:
            # empty sets are always subsets of other sets
            return True
        elif l > len(another_set):
            # subsets cannot be bigger than the target
            return False
        else:
            # note to self: this will be more efficent using temporary tables during mass scale operations
            return all(i in another_set for i in self)

    def issuperset(self, another_set):
        '''Report whether this set contains another set'''
        # see if we can short cut with len() alone
        if len(another_set) == 0:
            # empty sets are always subsets of other sets
            return True
        elif len(self) < len(another_set):
            # supersets cannot be bigger than the target
            return False
        else:
            # perf note: this will be more efficent using temporary tables during mass scale operations
            return all(i in self for i in another_set)


    def __iter__(self):
        '''Iterate through the values in the LiteSet'''
        query = self._cursor.execute(
            '''
                SELECT value FROM value_store
            '''
        )
        for value, in query:
            yield load(value)
    
    def __len__(self):
        query = self._cursor.execute('''
            select count(value) from value_store
        ''')
        for cnt, in query:
            return cnt
            
    def __str__(self):
        return str(set(self))
        
    def __repr__(self):
        return repr(set(self))
        
    def update(self, new_items_to_insert):
        '''Update a set with the union of itself and others'''
        # only ensure input is iterable because it might be another massive
        # LiteCollection that doesn't need to be completely in ram
        iter(new_items_to_insert)  # assert new_items_to_insert is iterable
        autocommit_before = self._autocommit
        try:
            self._autocommit = False
            # perf note: this would be faster with an insert many operation later
            for v in new_items_to_insert:
                self.add(v)
        finally:
            self._autocommit = autocommit_before
        if self._autocommit:
            self.commit()

    def union(self, another_set):
        '''Return the union of sets as a new LiteSet'''
        output = LiteSet(another_set)
        output.update(self)
        return output
    
    def intersection(self, another_set):
        '''Return the intersection of two sets as a new set.'''
        return LiteSet(i for i in another_set if i in self)
    
    def difference(self, other_set, *more_sets):
        '''Return the difference of two or more sets as a new set'''
        all_sets = other_set, *more_sets
        # tempted to build a new LiteSet here to compare against one
        # however that wont work well if the sets are massive.
        return LiteSet(i for i in self if not any(i in s for s in all_sets))

    def isdisjoint(self, other_set):
        '''Return True if two sets have a null intersection'''
        return not any(i in self for i in other_set)
    
    def symmetric_difference(self, other_set):
        '''Return all elements that are in exactly one of the sets as a new LiteSet'''
        return LiteSet(
            chain(
                (i for i in self if i not in other_set), 
                (i for i in other_set if i not in self)
            )
        )
    
    def copy(self, db_path=':memory:'):
        '''Returns a copy of this LiteSet with the given storage path'''
        assert isinstance(db_path, str), db_path
        if db_path == ':memory:':
            return LiteSet(self)
        else:
            self.backup(backup_path=db_path)
            return LiteSet(db_path=db_path)

    def difference_update(self, items_to_remove):
        '''Remove all elements of another set from this set'''
        iter(items_to_remove)  # assert items_to_remove is iterable
        autocommit_before = self._autocommit
        try:
            self._autocommit = False
            # perf note: this would be faster with an insert many operation later
            for v in items_to_remove:
                self.discard(v)
        finally:
            self._autocommit = autocommit_before
        if self._autocommit:
            self.commit()
    
    def intersection_update(self, items_to_intersect):
        '''Update a set with the intersection of itself and another'''
        iter(items_to_intersect)  # assert items_to_intersect is iterable
        autocommit_before = self._autocommit
        try:
            self._autocommit = False
            # perf note: this would be faster with an insert many operation later
            for v in self.difference(items_to_intersect):
                self.discard(v)
        finally:
            self._autocommit = autocommit_before
        if self._autocommit:
            self.commit()

    def symmetric_difference_update(self, other_set):
        '''Update a set with the symmetric difference of itself and another'''
        iter(other_set)  # assert other_set is iterable
        autocommit_before = self._autocommit
        try:
            self._autocommit = False
            # perf note: this would be faster with an insert many operation later
            symmetric_diff = self.symmetric_difference(other_set)
            self.clear()
            self.update(symmetric_diff)
            symmetric_diff.close()
        finally:
            self._autocommit = autocommit_before
        if self._autocommit:
            self.commit()
    
    __lte__ = issubset
    __gte__ = issuperset
    __or__ = union
    __and__ = intersection
    __sub__ = difference
