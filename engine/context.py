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

from pyseas.renderer import WebRenderContext
from .callbackRegistry import WebCallbackRegistry
from .contextDispatch import RequestContextDispatch

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Web View Context
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebViewContextBase(RequestContextDispatch):
    RenderContext = WebRenderContext
    CallbackRegistry = WebCallbackRegistry
    decorators = None

    def __init__(self):
        self._initViewContext()

    def _initViewContext(self):
        self._cbRegistryMap = self.CallbackRegistry.newRegistryMap()

    def findRootForRequest(self, request, nsCtx):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~ Composed objects request methods ~~~~~~~~~~~~~~~~~

    def findCallbackAndRegistry(self, request, default=False):
        """Finds registered callback for a valid request or None.  Second
        result is the callback registry to be passed into createRenderContext
        for registering new callbacks.
        
        Valid callback requests that are not found return default parameter."""
        cbRegistry = self._cbRegistryMap(request.path)
        reqCallback = cbRegistry.find(request.args, default)
        return reqCallback, cbRegistry

    def createRenderContext(self, request, cbRegistry, clear=False):
        """Creates a WebRenderContext bound to the callback registry for
        rendering the components."""
        if clear: 
            cbRegistry.clear()

        rctx = self.RenderContext(cbRegistry)
        if self.decorators:
            rctx.decorators.extend(self.decorators)
        return rctx

    #~ Render dispatch extension points ~~~~~~~~~~~~~~~~~

    def _renderComponentView(self, request, renderCtx, nsCtx):
        root = self.findRootForRequest(request, nsCtx)
        return renderCtx.render(root)
    def _renderCallbackView(self, request, renderCtx, cbResult):
        return renderCtx.autoRender(cbResult)

