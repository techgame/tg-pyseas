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

    context = None
    def __init__(self, context=None, fmtUrl=None):
        self.context = context
        if fmtUrl is not None:
            self.fmtUrl = fmtUrl

    def render(self, root, pretty_print=True):
        self.root = root
        r = root.renderOn(self)
        del self.root
        return self.tostring(r, pretty_print=pretty_print)

    def tostring(self, elem, *args, **kw):
        return etree.tostring(elem, *args, **kw)

    def __getattr__(self, key):
        return getattr(self.E, key)

