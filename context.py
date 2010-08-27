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

import uuid
import urlparse
import urllib

from .callbackRegistry import WebCallbackRegistryMap
from .renderContext import WebRenderContext

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ComponentRequestContext(object):
    ignoreResTypes = (float, int, long, complex)
    def __init__(self, csObj, requestPath, requestArgs):
        self.csObj = csObj
        self.cbReg = csObj.cbRegistryForPath(requestPath)
        self.requestPath = requestPath
        self.requestArgs = requestArgs

    def perform(self, component, **kw):
        r = self.callback()
        if r is None:
            r = self.render(component, **kw)
        return r

    def callback(self):
        callback = self.cbReg.find(self.requestArgs)
        if callback:
            res = callback()
            if res is None:
                return self.redirect()

            res = self.renderCallback(res)
            if not res or isinstance(res, self.ignoreResTypes):
                return self.redirect()

            return res

    def render(self, component, decorators=None, clear=True):
        if callable(component):
            component = component(self.csObj)

        if clear:
            self.cbReg.clear()
        wr = self.csObj.createRenderContext(self.cbReg, decorators)
        return wr.render(component)

    def renderCallback(self, res, decorators=None):
        wr = self.csObj.createRenderContext(self.cbReg, decorators)
        return wr.autoRender(res)

    def redirect(self):
        return self.csObj.redirect(self.requestPath)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SessionComponentContextManager(object):
    def __init__(self, ComponentContext, sessionKey):
        self.ComponentContext = ComponentContext
        self.sessionKey = sessionKey
        self.db = {}

    def lookup(self, session, orCreate=True):
        entryKey = session.get(self.sessionKey)
        entry = self.db.get(entryKey)
        if entry is not None:
            return entry

        if orCreate:
            entry = self.ComponentContext()
            entryKey = id(entry)
            self.db[entryKey] = entry
            session[self.sessionKey] = entryKey
        return entry

    def __contains__(self, session):
        return self.lookup(session, False)
    def __getitem__(self, session):
        return self.lookup(session, True)
    def get(self, session, default=None):
        r = self.lookup(session, False)
        if r is None:
            r = default
        return r

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Component Context
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebComponentContext(object):
    RenderContext = WebRenderContext
    RequestContext = ComponentRequestContext
    CallbackRegistryMap = WebCallbackRegistryMap

    def __init__(self):
        self._initContext()
        self.init()

    def _initContext(self):
        self.cbRegistryForPath = self.CallbackRegistryMap()

    def init(self):
        pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def redirect(self, url):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def createRenderContext(self, cbRegistry, decorators=None):
        wr = self.RenderContext(cbRegistry)
        if decorators:
            wr.decorators.extend(decorators)
        return wr

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def sessionManager(klass, sesionKey):
        return SessionComponentContextManager(klass, sesionKey)

    def context(self, request):
        return self.RequestContext(self, request.path, request.args)

