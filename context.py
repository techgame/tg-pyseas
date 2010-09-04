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

from contextlib import contextmanager
from .callbackRegistry import WebCallbackRegistryMap
from .renderContext import WebRenderContext

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ComponentRequestContext(object):
    ignoreResTypes = (float, int, long, complex)
    result = None
    executed = False

    def __init__(self, csObj, requestPath, requestArgs):
        self.csObj = csObj
        self.cbReg = csObj.cbRegistryForPath(requestPath)
        self.requestPath = requestPath
        self.requestArgs = requestArgs

    def __nonzero__(self):
        return self.result is None

    def asResult(self, res):
        self.result = res
        return res

    def perform(self, component, **kw):
        r = self.callback()
        if r is None:
            r = self.render(component, **kw)
        return r

    def callback(self):
        if self.executed:
            return self.result
        self.executed = True

        callback = self.cbReg.find(self.requestArgs, self.callbackMissing)
        if callback:
            res = callback()
            if res is None:
                return self.redirect()

            res = self.renderCallback(res)
            if not res or isinstance(res, self.ignoreResTypes):
                return self.redirect()

            return res

    def createRenderContext(self, decorators=None, clear=False):
        if clear: self.cbReg.clear()
        return self.csObj.createRenderContext(self.cbReg, decorators)

    def render(self, component, decorators=None, clear=True):
        if callable(component):
            component = component(self.csObj)

        rctx = self.createRenderContext(decorators, True)
        return self.asResult(rctx.render(component))

    def renderCallback(self, res, decorators=None):
        rctx = self.createRenderContext(decorators, False)
        return self.asResult(rctx.autoRender(res))

    def redirect(self):
        return self.asResult(self.csObj.redirect(self.requestPath))

    def callbackMissing(self):
        return self.asResult(self.csObj.callbackMissing(self.requestPath))

    @contextmanager
    def inRenderCtx(self, obj=None, decorators=None, clear=True):
        if not self.executed:
            self.callback()

        if self.result is None: 
            self.cbReg.clear()
            rctx = self.createRenderContext(decorators, clear)
            with rctx.inRenderCtx(obj) as renderer:
                yield renderer
            self.result = renderer.result()
        else:
            yield None

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
    def callbackMissing(self, url):
        return self.redirect(url)

    def createRenderContext(self, cbRegistry, decorators=None):
        rctx = self.RenderContext(cbRegistry)
        if decorators:
            rctx.decorators.extend(decorators)
        return rctx

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def sessionManager(klass, sesionKey):
        return SessionComponentContextManager(klass, sesionKey)

    def context(self, request):
        return self.RequestContext(self, request.path, request.args)

