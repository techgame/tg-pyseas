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

from lxml import etree

from .renderContext import BaseRenderer
from .htmlBrushContext import HtmlBrushContextApiMixin

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
        with page.renderHtmlCtxOn(self, self.decorators):
            r = page.renderHtmlOn(self)
            self.handleRenderResult(r)

    def _performRenderComponent(self, component):
        with component.renderHtmlCtxOn(self, self.decorators):
            r = component.renderHtmlOn(self)
            self.handleRenderResult(r)

    def renderNestedCtx(self, target, outer=None, inner=None):
        lst = []
        if outer: lst.extend(outer)
        if inner: lst.extend(inner)

        lst = [c.renderHtmlCtxTargetOn(self, target) for c in lst]
        return contextlib.nested(*lst)

    #~ rendering results ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def result(self, **kw):
        last = self._brushCtx.resultBrush()
        return last.__html__()

    def handleRenderResult(self, r):
        if r in (True, False): return

        if isinstance(r, basestring):
            self.raw(r)
        elif etree.iselement(r):
            self.lxml(r)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def autoRender(self, item, defaultTag=None):
        if getattr(item, 'isWebComponent', bool)():
            return self.render(item)
        else:
            return self._brushCtx.topBrush().addItem(item)

HtmlRenderer.registerRenderFactory('html', 'html5', 'xhtml')

