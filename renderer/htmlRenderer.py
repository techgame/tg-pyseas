##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2010  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

"""
with html.div():

    with html.p():
        html.strong('neato')
        html.space()
        html.text('keen')

    html.strong('neato')

    html.p(
        html.strong('neato'),
        html.space(),
        'keen')
"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import contextlib

from .baseRenderer import BaseRenderer
from .htmlBrush import HtmlBrushContextApiMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Html Rendering brushes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlRenderer(BaseRenderer, HtmlBrushContextApiMixin):
    tagBrushMap = None # use defaults
    decorators = None

    def _init(self, cbRegistry):
        self._initBrushContext(cbRegistry, self.tagBrushMap)

    #~ visitor concrete implementations ~~~~~~~~~~~~~~~~~ 

    def _performRenderPage(self, page):
        with page.renderCtxOn(self, self.decorators):
            r = page.renderHtmlOn(self)
            r = self.handleRenderResult(r)
        return r

    def _performRenderComponent(self, component):
        with component.renderCtxOn(self, self.decorators):
            r = component.renderHtmlOn(self)
            r = self.handleRenderResult(r)
        return r

    @contextlib.contextmanager
    def usingDecorators(self, decorators):
        prev = self.decorators
        self.decorators = decorators
        yield
        self.decorators = prev

    def _bindNestedCtx(self, target, ctxList):
        return [c.renderCtxHtmlOn(self, target) for c in ctxList]

    def inBrushRenderCtx(self, obj):
        return self._brushCtx.inBrushRenderCtx(obj)

    def render(self, component):
        with self.inBrushRenderCtx(component) as brush:
            r = component.renderOn(self.ctx)
            if r is None: r = brush
            return r

    #~ rendering results ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def result(self, **kw):
        return self.__html__()

    def __html__(self):
        return self._brushCtx.__html__()

    def handleRenderResult(self, r):
        if r in (None, True, False): return r

        if getattr(r, 'isWebComponent', bool)():
            return r
        if hasattr(r, '__html__'):
            self.raw(r)
        elif isinstance(r, basestring):
            self.raw(r)
        return r

    def autoRender(self, item, defaultTag=None):
        if getattr(item, 'isWebComponent', bool)():
            return self.render(item)
        else:
            return self.addItem(item)

    def __call__(self, tag, *args, **kw):
        if hasattr(tag, 'isWebComponent'):
            return self.render(tag)
        if callable(tag):
            return self.call(tag, *args, **kw)

        return self.createBrush(tag, *args, **kw)

    def call(self, fn, *args, **kw):
        with self.collection() as brush:
            r = fn(self, *args, **kw)
            if r is None: r = brush
            return r

HtmlRenderer.registerRenderFactory('html', 'html5', 'xhtml')

