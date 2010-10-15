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

import contextlib
from .renderContext import WebRenderContext

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

    def renderNestedCtx(self, target, outer=None, inner=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseRenderer(AbstractRenderer):
    def __init__(self, ctx, cbRegistry):
        self.ctx = ctx
        self._init(cbRegistry)

    def _init(self, cbRegistry):
        pass

    def render(self, component):
        return component.renderOn(self.ctx)

    @classmethod
    def registerRenderFactory(klass, *outputKeys):
        WebRenderContext.registerRenderFactory(klass, *outputKeys)

    def autoRender(self, item):
        if getattr(item, 'isWebComponent', bool)():
            return self.render(item)
        else: return item

    def renderNestedCtx(self, target, *ctxListArgs):
        ctxList = []
        for e in ctxListArgs:
            if e: ctxList.extend(e)
        ctxList = self._bindNestedCtx(target, ctxList)
        return contextlib.nested(*ctxList)

    def _bindNestedCtx(self, target, ctxList):
        return ctxList

