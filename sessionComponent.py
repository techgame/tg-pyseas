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
from itertools import islice

from .component import WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Object Sessions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectSessions(object):
    Factory = None

    def __init__(self, sessionKey, session):
        self._initSession(sessionKey, session)
        self._initCollection()

    def bindFactory(self, factory, *args, **kw):
        if args or kw:
            factory = functools.partial(factory, *args, **kw)
        self.Factory = factory

    def lookup(self, orCreate=True):
        key = self.getEntrySessionKey()
        entry = self.fetchEntry(key)
        if entry is not None:
            return entry

        if orCreate:
            key, entry = self.createEntry()
            self.setEntrySessionKey(key)
        return entry
    __call__ = lookup

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _initSession(self, sessionKey, session):
        self.sessionKey = sessionKey
        self.session = session
    def getEntrySessionKey(self):
        return self.session.get(self.sessionKey)
    def setEntrySessionKey(self, key):
        self.session[self.sessionKey] = key
        return key

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
        print 'retire:', entry


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SessionComponent(WebComponent):
    ObjectSessions = ObjectSessionsMRU

    def __init__(self, sessionKey, session, factory=None):
        self.objSessions = self.ObjectSessions(sessionKey, session)
        if factory is not None:
            self.bindFactory(factory)

    def bindFactory(self, factory, *args, **kw):
        return self.objSessions.bindFactory(factory, *args, **kw)
    def lookup(self, orCreate=True):
        return self.objSessions.lookup(orCreate)

    def renderHtmlOn(self, html):
        target = self.lookup()
        html.render(target)

    def updateMRU(self, interval=60, length=4):
        return self.objSessions.udpateM(interval, length)

