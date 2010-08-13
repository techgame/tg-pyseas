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

from lxml import etree
import lxml.html.builder

from .renderBase import WebRendererBase

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebRenderer(WebRendererBase):
    E = lxml.html.builder.E
    E.XML = etree.XML

    def tostring(self, elem, *args, **kw):
        return etree.tostring(elem, *args, **kw)

    def __getattr__(self, key):
        return getattr(self.E, key)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def render(self, root, pretty_print=True):
        self.root = root
        r = root.renderOn(self)
        del self.root
        return self.tostring(r, pretty_print=pretty_print)

    def composedRenderOn(E, target):
        r = target.renderHTMLOn(E)
        if r is None: 
            raise RuntimeError("%s failed to return rendered output"%(target.__class__,))

        r = target.renderHTMLAfterOn(E, r)
        if r is None: 
            raise RuntimeError("%s failed to return rendered after output"%(target.__class__,))

        r = E.renderDecoratedHTMLOn(target, r)
        return r

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _decorators = None
    def getDecorators(self):
        r = self._decorators
        if r is None:
            self._decorators = r = []
        return r
    decorators = property(getDecorators)

    def renderDecoratedHTMLOn(self, target, r):
        decorators = self._decorators or ()
        for deco in decorators:
            r = deco.renderDecoratedHTMLOn(target, self, r)
        return r

    def renderHTMLAfterOn(self, E, r):
        return r

