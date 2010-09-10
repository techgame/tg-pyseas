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

import functools
from .component import WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Object Sessions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectSessions(object):
    CollectionFactory = dict
    Factory = None

    def __init__(self, sessionKey, session):
        self.objdb = self.CollectionFactory()
        self.sessionKey = sessionKey
        self.session = session

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

    def fetchEntry(self, key):
        return self.objdb.get(key)

    def createEntry(self):
        entry = self.Factory()
        key = id(entry)
        self.objdb[key] = entry
        return key, entry

    def getEntrySessionKey(self):
        return self.session.get(self.sessionKey)
    def setEntrySessionKey(self, key):
        self.session[self.sessionKey] = key
        return key

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SessionComponent(WebComponent):
    ObjectSessions = ObjectSessions

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

