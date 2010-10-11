##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2010  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import types

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def url_attrs(*args, **kw):
    attrs = dict(*args, **kw)
    def tag_attrs_decorator(fn):
        fn.attrs = attrs
        return fn
    return tag_attrs_decorator

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class IdCounters(object):
    fmt = '%s-%s'
    def __init__(self, fmt=None):
        if fmt is not None:
            self.fmt = fmt
        self._db = {}

    def counter(self, prefix, idx=0):
        fmt = self.fmt
        while 1:
            yield fmt%(prefix, idx)
            i += 1

    def __contains__(self, key):
        return key in self._db
    def get(self, key, default=None):
        v = self._db.get(key)
        if v is None:
            return default
        else: return v()
    def __getitem__(self, key):
        v = self._db.get(key)
        if v is None:
            v = self.counter(key, idx).next
            self._db[key] = v
        return v()
    def __getattr__(self, key):
        return self[key]
    def __call__(self, key):
        return self[key]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class objectmethod(object):
    factory = types.MethodType

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __get__(self, obj, klass=None):
        if obj is None: obj = klass
        return self.factory(self.func, obj, klass)

