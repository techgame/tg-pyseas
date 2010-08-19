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
from .component import WebComponentBase
from .listComponent import WebListPartsMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebPageHeader(object):
    title = None

    def __init__(self, title=None):
        if title is not None:
            self.title = title
        self.links = set()
        self._parts = []
    def copy(self):
        r = self.__class__()
        r.title = self.title
        r.links = self.links.copy()
        r._parts = self._parts[:]
        return r

    def add(self, key, content=None, **attrib):
        if key == 'link':
            raise ValueError("Use addLink to add header links")
        self._parts.append((key, content, attrib))
    def addMeta(self, **attrib):
        self._parts.append(('meta', None, attrib))
    def addScript(self, content, **attrib):
        self._parts.append(('script', content, attrib))
    def addStyle(self, content, **attrib):
        self._parts.append(('style', content, attrib))
    def addBase(self, href=None, target=None):
        ns = {}
        if href is not None:
            ns['href'] = href
        if target is not None:
            ns['target'] = target
        if not ns:
            raise ValueError("Expected href or target parameter")

        self._parts.append(('base', None, ns))

    def addLink(self, href, rel, type):
        if href in self.links:
            return
        ns = dict(href=href, rel=rel, type=type)
        self._parts.append(('link', None, ns))
        self.links.add(href)
    link = addLink
    def addStylesheet(self, href, rel='stylesheet'):
        return self.addLink(href, rel, 'text/css')
    stylesheet = addStylesheet

    def asHTML(self, html):
        head = html.head()
        add = head.append
        if self.title:
            add(html.title(self.title))

        for key, content, attrib in self._parts:
            if content is not None:
                add(html(key, content, **attrib))
            else:
                add(html(key, **attrib))
        return head

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Page Component that adds header to the context
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebPageComponent(WebListPartsMixin, WebComponentBase):
    title = None
    def __init__(self, title=None):
        if title is not None:
            self.title = title

    def renderOn(self, rctx):
        return rctx.pageRenderOn(self)

    def renderHTMLOn(self, rctx, html):
        rctx.header = self.header.copy()
        body = html.body()
        self.renderPartsOn(body, rctx)

        # render the header after the body, in case 
        # another component modified it in rctx
        header = rctx.header.asHTML(html)
        return html.html(header, body)

    _header = None
    def getHeader(self):
        r = self._header
        if r is None:
            r = WebPageHeader(self.title)
            self._header = r
        return r
    header = property(getHeader)

