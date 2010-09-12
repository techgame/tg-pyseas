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

import os
import time
import functools
import collections
from hashlib import md5
from itertools import islice

from .component import WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Object Sessions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectSessions(object):
    Factory = None

    def __init__(self, factory=None, *args, **kw):
        self._initCollection()
        if factory is not None:
            self.bindFactory(factory, *args, **kw)

    def bindFactory(self, factory, *args, **kw):
        if args or kw:
            factory = functools.partial(factory, *args, **kw)
        self.Factory = factory
        self._assignUniqueAttrKey(factory)
    bind = bindFactory

    def _assignUniqueAttrKey(self, factory):
        tgt = factory
        while not hasattr(tgt, '__module__'):
            tgt = tgt.func

        key = md5(tgt.__module__+':'+tgt.__name__)
        # use only 1/2 of the digits
        key = key.digest()[:9] 
        key = key.encode('base64').rstrip()
        self.uniqueAttrKey = '~pi-'+key

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def bindLookup(self, session):
        def lookup(orCreate=True):
            return self.lookup(session, orCreate)
        return lookup

    def lookup(self, session, orCreate=True):
        key = session.get(self.uniqueAttrKey, None)
        if key is not None:
            entry = self.fetchEntry(key)
            if entry is not None:
                return entry

        if orCreate:
            key, entry = self.createEntry()
            session[self.uniqueAttrKey] = key
        return entry
    __call__ = lookup

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _initCollection(self):
        self._entryDB = {}

    def fetchEntry(self, key):
        return self._entryDB.get(key)

    def createEntry(self):
        entry = self.Factory()
        key = id(entry)
        self._entryDB[key] = entry
        return key, entry

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectSessionsMRU(ObjectSessions):
    if os.name.startswith('win'):
        timestamp = staticmethod(time.clock)
    else: timestamp = staticmethod(time.time)

    mruInterval = 300
    mruLength = 4
    _mruTSNext = 0

    def updateMRU(self, interval=60, length=4):
        self.mruInterval = interval
        self.mruLength = length

    def _initCollection(self):
        self._entry_mru = collections.deque()
        self._entry_mru.append({})

    def _serviceMRU(self):
        self._mruTSNext = self.timestamp() + self.mruInterval

        entry_mru = self._entry_mru
        entry_mru.appendleft({})
        if len(entry_mru) <= self.mruLength:
            return False

        entryDB = entry_mru.pop()
        for entry in entryDB.itervalues():
            self.retireEntry(entry)
        return True

    def fetchEntry(self, key):
        topEntryDB = self._entry_mru[0]
        entry = topEntryDB.get(key)
        if entry is None:
            entry = self.faultEntry(key, topEntryDB)

        if self.timestamp() > self._mruTSNext:
            self._serviceMRU()
        return entry

    def faultEntry(self, key, topEntryDB):
        # fault the entry from inside the MRU
        for entryDB in islice(self._entry_mru, 1):
            entry = entryDB.pop(key, None)
            if entry is not None:
                topEntryDB[key] = entry
                break

    def createEntry(self):
        entry = self.Factory()
        key = id(entry)
        self._entry_mru[0][key] = entry
        return key, entry

    def retireEntry(self, entry):
        pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def bindSessionFactory(session, factory, *args, **kw):
    if kw.pop('mruSession', True):
        objSessions = ObjectSessionsMRU(factory, *args, **kw)
    else:
        objSessions = ObjectSessions(factory, *args, **kw)
    return objSessions.bindLookup(session)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SessionComponent(WebComponent):
    ObjectSessions = ObjectSessionsMRU
    session = None

    def __init__(self, factory=None, *args, **kw):
        self.objSessions = self.ObjectSessions()
        if factory is not None:
            self.objSessions.bindFactory(factory, *args, **kw)

    def renderHtmlOn(self, html):
        target = self.objSessions.lookup(self.session)
        html.render(target)

