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

from .callbackRegistry import WebCallbackRegistry
from .renderContext import WebRenderContext

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RequestContextDispatch(object):
    ignoreResultTypes = set([type(None), bool, float, int, long, complex])

    #~ Composed objects request methods ~~~~~~~~~~~~~~~~~

    def findCallbackAndRegistry(self, request, default=False):
        """Finds registered callback for a valid request or None.  Second
        result is the callback registry to be passed into createRenderContext
        for registering new callbacks.
        
        Valid callback requests that are not found return default parameter."""
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def createRenderContext(self, request, cbRegistry, clear=False):
        """Creates a WebRenderContext bound to the callback registry for
        rendering the components."""
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~ Dispatch request composed method ~~~~~~~~~~~~~~~~~

    def dispatchRequest(self, request, **nsCtx):
        return self._performDispatch(request, nsCtx)

    def _performDispatch(self, request, nsCtx):
        """Performs component dispatch, including registered callbacks"""
        # find if there is a registered callback for the request arguments
        reqCallback, cbRegistry = self.findCallbackAndRegistry(request, False)

        if reqCallback is None:
            # perform normal component dispatch rendering
            renderCtx = self.createRenderContext(request, cbRegistry, True)
            return self._renderComponentView(request, renderCtx, nsCtx)

        if reqCallback is False:
            # the callback referenced correctly, but missing.
            return self._renderCallbackMissing(request)

        # perform registered callback
        cbResult = reqCallback()

        # render the callback's cbResult to support AJAX style components
        return self._renderCallbackResult(request, cbRegistry, cbResult)

    def _renderCallbackResult(self, request, cbRegistry, cbResult):
        if type(cbResult) not in self.ignoreResultTypes:
            # if there useful cbResult, create a render context
            renderCtx = self.createRenderContext(request, cbRegistry, False)
            # render the callback cbResult
            cbResult = self._renderCallbackView(request, renderCtx, cbResult)
            if type(cbResult) not in self.ignoreResultTypes:
                return cbResult
        # otherwise, perform redirect to the request path
        return self._renderCallbackRedirect(request)


    #~ Render dispatch extension points ~~~~~~~~~~~~~~~~~

    def _renderComponentView(self, request, renderCtx, nsCtx):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def _renderCallbackView(self, request, renderCtx, cbResult):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def _renderCallbackMissing(self, request):
        # test for AJAX request and return a 404 instead of redirect
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def _renderCallbackRedirect(self, request):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

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

