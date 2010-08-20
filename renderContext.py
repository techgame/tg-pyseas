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

from .callbackMap import WebCallbackMap, CallbackRegistrationMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebRenderContext(object):
    outputKey = 'html'
    context = None

    def __init__(self, cbRegistry, context=None, outputKey=None):
        if cbRegistry is None:
            cbRegistry = WebCallbackMap()
        self.cbRegistry = cbRegistry
        if context is not None:
            self.context = context
        if outputKey is not None:
            self.outputKey = outputKey

        self.decorators = []

    def render(self, root):
        self.renderer = self.createRenderer()
        root.renderOn(self)
        return self.renderer.result()

    def renderPage(self, page):
        return self.renderer._performRenderPage(page)
    def renderComponent(self, component):
        return self.renderer._performRenderComponent(component)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def createRenderer(self):
        factory = self.RenderFactoryMap[self.outputKey]
        renderer =  factory(self, self.cbRegistry)
        renderer.decorators = self.decorators
        return renderer

    @classmethod
    def registerRenderFactory(klass, RenderFactory, *outputKeys):
        for key in outputKeys:
            klass.RenderFactoryMap[key] = RenderFactory
    RenderFactoryMap = {}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AbstractRenderer(object):
    #~ visitor double dispatch pattern ~~~~~~~~~~~~~~~~~~

    def _performRenderPage(self, page):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def _performRenderComponent(self, component):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def render(self, component):
        return component.renderOn(self._rctx)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseRenderer(AbstractRenderer, CallbackRegistrationMixin):
    def __init__(self, rctx, cbRegistry):
        self._rctx = rctx
        self._cbRegistry = cbRegistry
        self._init()

    def _init(self):
        pass

    def callback(self, callback, context=None):
        if context is None:
            context = self._rctx.context
        return self._cbRegistry.add(callback, context)

    @classmethod
    def registerRenderFactory(klass, *outputKeys):
        WebRenderContext.registerRenderFactory(klass, *outputKeys)

