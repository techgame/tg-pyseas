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
#~ Page Component that adds header to the context
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebPageComponent(WebListPartsMixin, WebComponentBase):
    title = None
    def __init__(self, title=None):
        if title is not None:
            self.title = title

    def renderOn(self, rctx):
        return rctx.renderPage(self)

    def renderHTMLOn(self, html):
        html.pageHeader = self.pageHeader.copy()
        with html.html():
            head = html.head()
            with html.body():
                self.renderParts(html)

            # render the header after the body, in case 
            # another component modified it in rctx
            html.pageHeader.renderHTMLOnHead(html, head)

    _pageHeader = None
    def getPageHeader(self):
        r = self._pageHeader
        if r is None:
            r = WebPageHeader(self.title)
            self._pageHeader = r
        return r
    pageHeader = property(getPageHeader)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Page Header
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
        if not isinstance(key, basestring):
            raise ValueError("Key must be a string")
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

    def renderHTMLOnHead(self, html, head):
        with head:
            if self.title:
                html.title(self.title)

            for key, content, attrib in self._parts:
                if content is not None:
                    html(key, content, **attrib)
                else:
                    html(key, **attrib)

