#!/usr/bin/env python
# -*- coding: utf-8 -*-

# base collection class
from .LiteCollection import LiteCollection

# custom exceptions
from .LiteExceptions import InvalidPositionalArgCount

# LiteCollection subclasses and their exceptions
from .LiteDict import LiteDict
from .LiteSet import LiteSet, EmptyLiteSet

''' litecollections is a python library that
    takes every core python container structure
    and backs it with sqlite for mass scale
    data operations using generic python datatypes
'''
