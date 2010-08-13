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

from .component import WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebPageComponent(WebComponent):
    def renderHTMLOn(self, E):
        head = E.head()
        head.extend(E.E(k, **ns) for k,ns in self.head)

        body = E.body()
        for p in self.parts:
            body.append(p.renderOn(E))

        return E.html(head, body)

    def addHead(self, name, **ns):
        self.head.append((name, ns))
    def addLink(self, href, rel, type):
        self.addHead('link', href=href, rel=rel, type=type)
    def addStylesheet(self, href):
        return self.addLink(href, 'stylesheet', 'text/css')

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

    _head = None
    def getHead(self):
        r = self._head
        if r is None:
            self._head = r = []
        return r
    head = property(getHead)

