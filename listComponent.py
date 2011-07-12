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

from .adaptor import AdaptableMixin
from .component import WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebPartsMixin(object):
    def renderParts(self, html):
        for p in self.parts:
            html.render(p)

    _parts = None
    def getParts(self):
        r = self._parts
        if r is None:
            self._parts = r = []
        return r
    parts = property(getParts)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebListPartsMixin(WebPartsMixin, AdaptableMixin):
    def __len__(self):
        return len(self.parts)
    def __iter__(self):
        return iter(self.parts)
    def insert(self, idx, item):
        item = self.itemAsComponent(item)
        return self.parts.insert(idx, item)
    def remove(self, item):
        return self.parts.remove(item)
    def pop(self, item):
        return self.parts.pop(item)
    def sort(self, *args, **kw):
        return self.parts.sort(*args, **kw)

    def add(self, item):
        item = self.itemAsComponent(item)
        self.parts.append(item)
        return item
    append = add
    def extend(self, iterable):
        for item in iterable:
            self.add(item)
    def clear(self):
        self.parts[:] = []

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebListComponent(WebListPartsMixin, WebComponent):
    def renderHtmlOn(self, html):
        self.renderParts(html)

