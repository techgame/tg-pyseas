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
from .callbackRegistry import WebCallbackRegistryMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebRenderContext(object):
    outputKey = 'html'

    def __init__(self, cbRegistry, outputKey=None):
        if cbRegistry is None:
            cbRegistry = WebCallbackRegistry()
        self.cbRegistry = cbRegistry
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
#~ Renderer Base Classes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AbstractRenderer(object):
    #~ visitor double dispatch pattern ~~~~~~~~~~~~~~~~~~

    def _performRenderPage(self, page):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def _performRenderComponent(self, component):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def render(self, component):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseRenderer(AbstractRenderer):
    def __init__(self, rctx, cbRegistry):
        self._rctx = rctx
        self._init(cbRegistry)

    def _init(self, cbRegistry):
        pass

    def render(self, component):
        return component.renderOn(self._rctx)

    @classmethod
    def registerRenderFactory(klass, *outputKeys):
        WebRenderContext.registerRenderFactory(klass, *outputKeys)

