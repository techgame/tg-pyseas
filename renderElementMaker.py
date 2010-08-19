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
    html = lxml.html.builder.E
    html.XML = etree.XML
    html.HTML = etree.XML

    tostring = staticmethod(etree.tostring)

    def render(self, root, pretty_print=True):
        self.root = root
        result = root.renderOn(self)
        del self.root
        return self.tostring(result, pretty_print=pretty_print)

    def pageRenderOn(self, target):
        return target.renderHTMLOn(self, self.html)
    def componentRenderOn(self, target):
        result = target.renderHTMLOn(self, self.html)
        if result is None: 
            raise RuntimeError("%s failed to return rendered output"%(target.__class__,))

        result = target.renderHTMLAfterOn(self, self.html, result)
        if result is None: 
            raise RuntimeError("%s failed to return rendered after output"%(target.__class__,))

        result = self.renderDecoratedHTMLOn(target, result)
        return result

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _decorators = None
    def getDecorators(self):
        r = self._decorators
        if r is None:
            self._decorators = r = []
        return r
    decorators = property(getDecorators)

    def renderDecoratedHTMLOn(self, target, result):
        decorators = self._decorators or ()
        for deco in decorators:
            result = deco.renderDecoratedHTMLOn(target, self, self.html, result)
        return result

    def renderHTMLAfterOn(self, html, r):
        return r

