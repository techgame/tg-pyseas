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

from collections import defaultdict
from .component import WebComponentBase, WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebPageHeader(object):
    def __init__(self):
        self.parts = set()
    def copy(self):
        r = self.__class__()
        r.parts = self.parts.copy()
        return r

    def add(self, name, **ns):
        ns = tuple(sorted(ns.items()))
        self.parts.add((name, ns))

    def addLink(self, href, rel, type):
        self.add('link', href=href, rel=rel, type=type)
    link = addLink
    def addStylesheet(self, href, rel='stylesheet'):
        return self.addLink(href, rel, 'text/css')
    stylesheet = addStylesheet

    def asHTML(self, E):
        head = E.E.head()
        head.extend(E.E(k, **dict(ns)) for k,ns in self.parts)
        return head

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebPageComponent(WebComponent):
    def renderHTMLOn(self, E):
        E.header = self.header.copy()
        body = E.body()
        for p in self.parts:
            body.append(p.renderOn(E))

        return E.html(E.header.asHTML(E), body)

    def add(self, item):
        self.parts.append(item)
        return item

    _parts = None
    def getParts(self):
        r = self._parts
        if r is None:
            self._parts = r = []
        return r
    parts = property(getParts)

    _header = None
    def getHeader(self):
        r = self._header
        if r is None:
            r = WebPageHeader()
            self._header = r
        return r
    header = property(getHeader)

