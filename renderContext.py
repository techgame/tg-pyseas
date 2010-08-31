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
from contextlib import contextmanager

from .callbackRegistry import WebCallbackRegistry

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebRenderContext(object):
    outputKey = 'html'
    renderer = None

    def __init__(self, cbRegistry, outputKey=None):
        if cbRegistry is None:
            cbRegistry = WebCallbackRegistry()
        self.cbRegistry = cbRegistry
        if outputKey is not None:
            self.outputKey = outputKey

        self.decorators = []

    def render(self, root):
        if root is None: return
        renderOn = getattr(root, 'renderOn', root)

        with self.inRenderCtx(root) as renderer:
            renderOn(self)
            return renderer.result()

    def autoRender(self, item):
        if getattr(item, 'isWebComponent', bool)():
            return self.render(item)
        else: return item

    def renderPage(self, page):
        return self.renderer._performRenderPage(page)
    def renderComponent(self, component):
        return self.renderer._performRenderComponent(component)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @contextmanager
    def inRenderCtx(self, obj):
        previous = self.renderer
        renderer = self.createRenderer()
        self.renderer = renderer
        yield renderer
        self.renderer = previous

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

    def result(self, **kw):
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

    def autoRender(self, item):
        if getattr(item, 'isWebComponent', bool)():
            return self.render(item)
        else: return item

