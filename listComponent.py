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

from .component import WebComponentBase, WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebPartsMixin(object):
    def renderHTMLOn(self, rctx, html):
        return self.renderPartsOn(html.div(), rctx)

    def iterRenderParts(self, rctx):
        return (p.renderOn(rctx) for p in self.parts)
    def renderPartsOn(self, elem, rctx):
        elem.extend(self.iterRenderParts(rctx))
        return elem

    _parts = None
    def getParts(self):
        r = self._parts
        if r is None:
            self._parts = r = []
        return r
    parts = property(getParts)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebListPartsMixin(WebPartsMixin):
    def __len__(self):
        return len(self.parts)
    def __iter__(self):
        return iter(self.parts)
    def insert(self, idx, item):
        if not item.isWebComponent():
            raise ValueError("Expected an object implementing web component protocol")
        return self.parts.insert(idx, item)
    def remove(self, item):
        return self.parts.remove(item)
    def pop(self, item):
        return self.parts.pop(item)
    def sort(self, *args, **kw):
        return self.parts.sort(*args, **kw)

    def add(self, item):
        if not item.isWebComponent():
            raise ValueError("Expected an object implementing web component protocol")
        self.parts.append(item)
        return item
    append = add
    def extend(self, iterable):
        for item in iterable:
            self.add(item)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebListComponent(WebListPartsMixin, WebComponent):
    pass

