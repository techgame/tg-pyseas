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

import itertools
import contextlib
from functools import partial

from lxml import etree

from .renderContext import BaseRenderer
from .htmlBrushes import htmlTagBrushMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Html Rendering brushes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlRenderer(BaseRenderer):
    decorators = None
    def _init(self):
        self._stack = []

    #~ visitor concrete implementations ~~~~~~~~~~~~~~~~~ 

    def _performRenderPage(self, page):
        with page.renderHTMLCtxOn(self, self.decorators):
            r = page.renderHTMLOn(self)
            self.handleRenderResult(r)

    def _performRenderComponent(self, component):
        with component.renderHTMLCtxOn(self, self.decorators):
            r = component.renderHTMLOn(self)
            self.handleRenderResult(r)

    def renderNestedCtx(self, target, outer=None, inner=None):
        lst = []
        if outer: lst.extend(outer)
        if inner: lst.extend(inner)

        lst = [c.renderHTMLCtxTargetOn(self, target) for c in lst]
        return contextlib.nested(*lst)

    #~ stack ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def topBrush(self):
        stack = self._stack
        if stack: return stack[-1]

    def pushBrush(self, brush=None):
        self._stack.append(brush)
        return brush

    def popBrush(self):
        brush = self._stack.pop()
        self._currentBrush = brush
        return brush

    _currentBrush = None
    def onBrushCreated(self, brush):
        tb = self.topBrush()
        if tb is not None:
            tb.addImplicitBrush(brush)
        self._currentBrush = brush
        return tb

    #~ brushes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    tagBrushMap = htmlTagBrushMap
    def bindBrush(self, tag):
        brush = self.tagBrushMap.get(tag)
        if brush is None:
            raise LookupError("Brush %r not found"%(tag,), tag)
        return partial(brush, self, tag)

    def __call__(self, key, *args, **kw):
        brush = self.bindBrush(key)
        return brush(*args, **kw)
    def __getattr__(self, key):
        if not key.startswith('_'):
            try:
                return self.bindBrush(key)
            except LookupError, err:
                raise AttributeError(*err.args)

        else: raise AttributeError(key)

    def result(self, **kw):
        last = self.topBrush()
        if last is None:
            last = self._currentBrush

        return last.asXMLString(**kw)

    def handleRenderResult(self, r):
        if r in (True, False): return

        if isinstance(r, basestring):
            self.raw(r)
        elif etree.iselement(r):
            self.lxml(r)

HtmlRenderer.registerRenderFactory('html', 'html5', 'xhtml')

