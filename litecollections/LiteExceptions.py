
class InvalidPositionalArgCount(TypeError):
    '''raised when an invalid positional arg count is passed in'''

class EmptyLiteSet(KeyError):
    '''raised when trying to pull a key from an empty LiteSet'''

class AlreadyActiveDBPath(ValueError):
    '''raised when trying to write a new LiteCollections object to an already active LiteCollections database'''

class InvalidBackupPath(ValueError):
    '''raised when trying to back up a LiteCollections object to an illegal os path'''
