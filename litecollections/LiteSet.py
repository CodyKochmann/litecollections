#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
            # the normal dict() constructor behavior
            self.update(set(*set_args))
        
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
        
    def update(self, update_set):
        assert isinstance(update_set, dict), update_set
        autocommit_before = self._autocommit
        try:
            self._autocommit = False
            for v in update_set:
                self.add(v)
        finally:
            self._autocommit = autocommit_before
        if self._autocommit:
            self.commit()
