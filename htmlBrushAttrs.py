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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def asMultiValueKeys(names, sep=' '):
    if hasattr(names, 'get'):
        return names
    if isinstance(names, basestring):
        names = names.split()
    return dict.fromkeys(names, sep)

def updateMultiValueKeyMap(mvKeyMap):
    for k, v in mvKeyMap.iteritems():
        mvKeyMap[k] = asMultiValueKeys(v)
    return mvKeyMap

tagMultiValueKeyMap = {
    'a': {'class':' ', 'rel': ' ', 'ping': ' ', 'style': '; '},
    None: {'class':' ', 'rel': ' ', 'style': '; '},
}

updateMultiValueKeyMap(tagMultiValueKeyMap)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ HTML Brush Attrs
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlBrushAttrs(object):
    slots = ['ns']
    _tagMultiValueKeyMap = tagMultiValueKeyMap
    _multiValueKeys = _tagMultiValueKeyMap[None]

    def __init__(self, *args, **kw):
        self._ns = {}
        if args or kw:
            self.update(*args, **kw)

    def tagInstance(self, tag, multiValueKeys=None):
        self = self.copy()
        mvk = multiValueKeys
        if mvk is None:
            mvkMap = self._tagMultiValueKeyMap
            mvk = mvkMap.get(tag)
            if mvk is None:
                mvk = mvkMap[None]

        self._multiValueKeys = asMultiValueKeys(mvk)
        return self

    def asAttrMap(self):
        return self._ns
    def asKey(self, key):
        return key.rstrip('_')

    def copy(self):
        return self.__class__(self._ns)
    def branch(self, *args, **kw):
        r = self.copy() 
        r.update(*args, **kw)
        return r

    def __getattr__(self, key):
        if key.startswith('_'):
            return object.__getattr__(self, key)
        return self.get(key)
    def __setattr__(self, key, value):
        if key.startswith('_'):
            return object.__setattr__(self, key, value)
        self[key] = value
    def __delattr__(self, key):
        if key.startswith('_'):
            return object.__delattr__(self, key)
        del self[key]

    def set(self, key, value):
        self._ns[key] = value
    def add(self, key, value, sep=None):
        if sep is None:
            sep = self._multiValueKeys.get(key, ' ')

        ns = self._ns
        if key in ns:
            value = sep.join([ns[key], value])
        ns[key] = value
        return value
    def discard(self, key, value, sep=None):
        if sep is None:
            sep = self._multiValueKeys.get(key)
        r = self[key].split(sep)
        r[:] = [e for e in r if e != value]
        r = sep.join(r)
        return r

    def update(self, *args, **kw):
        set = self.__setitem__
        for k,v in dict(*args, **kw).items():
            set(k, v)

    def clear(self):
        self._ns.clear()
    def setdefault(self, key, default):
        key = self.asKey(key)
        if key not in self._ns:
            self[key] = default
        return self[key]
    def pop(self, key, default=None):
        key = self.asKey(key)
        return self._ns.pop(key, None)
    def popitem(self):
        return self._ns.popitem()

    def __len__(self):
        return len(self._ns)
    def __iter__(self):
        return self._ns.iteritems()
    def __contains__(self, key):
        key = self.asKey(key)
        return key in self._ns
    has_key = __contains__
    def get(self, key, default=None):
        key = self.asKey(key)
        return self._ns.get(key, default)
    def __getitem__(self, key):
        key = self.asKey(key)
        return self._ns[key]
    def __setitem__(self, key, value):
        ns = self._ns
        key = self.asKey(key)
        if key in ns:
            # check for multi-value keys (usually space seperated)
            sep = self._multiValueKeys.get(key)
            if sep:
                value = sep.join(ns[key], value)
        ns[key] = value
    def __delitem__(self, key):
        key = self.asKey(key)
        self._ns.pop(key, None)

    def keys(self): return self._ns.keys()
    def values(self): return self._ns.values()
    def items(self): return self._ns.items()
    def iterkeys(self): return self._ns.iterkeys()
    def itervalues(self): return self._ns.itervalues()
    def iteritems(self): return self._ns.iteritems()


