#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

from .LiteExceptions import AlreadyActiveDBPath, InvalidBackupPath

class LiteCollection(object):
    ''' base class for sqlite backed collection objects '''
    _default_db_path = ':memory:'
    _default_autocommit = True
    
    def __init__(self, schema, db_path=_default_db_path):
        assert isinstance(schema, list), schema
        assert isinstance(db_path, str), db_path
        self._schema = schema
        self._db_path = db_path
        self._autocommit = LiteCollection._default_autocommit
        self._db = sqlite3.connect(self._db_path)
        self._cursor = self._db.cursor()
        
        self.commit = self._db.commit
        self.iterdump = self._db.iterdump
        
        for command in self._schema:
            assert isinstance(command, str), command
            self._cursor.execute(command)
    
    def close(self):
        self._db.commit()
        self._cursor.close()
        self._db.close()

    @property
    def autocommit(self):
        return self._autocommit
        
    @autocommit.setter
    def autocommit(self, value):
        assert value in {True, False}, value
        self._autocommit = value
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        ''' automatically close up everything with context managers '''
        self.close()

    def backup(self, backup_path:str):
        ''' creates a backup sqlite database at the given path '''
        assert isinstance(backup_path, str), backup_path
        if backup_path == ':memory:':
            raise InvalidBackupPath('Cannot write database backup to the file path ":memory:" If you are trying to deep copy the object, just create another instance with the LiteCollection you are trying to copy as the first argument.')
        elif backup_path == self._db_path:
            raise AlreadyActiveDBPath(f'cannot run backup() to the same active db path {db_path} used in this object')
        else:
            bck = sqlite3.connect(backup_path)
            try:
                with bck:
                    self._db.backup(bck)
            finally:
                bck.close()
