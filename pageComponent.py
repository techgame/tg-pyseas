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

from .htmlBrushContext import HtmlBrushContextApiMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Page Component that adds header to the context
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebPageComponent(WebListPartsMixin, WebComponentBase):
    def __init__(self, title=None, *parts):
        parts = list(parts)
        if getattr(title, 'isWebComponent', bool)():
            parts.insert(0, title)
            title = None

        if title is not None:
            self.title = title

        if parts:
            self.extend(parts)

    def renderOn(self, rctx):
        return rctx.renderPage(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def renderHTMLOn(self, html):
        pageHeader = self.pageHeader.copy()
        with html.html():
            head = pageHeader.startRenderHeader(html)

            with html.body():
                self.renderPageBodyOn(html)

            # render the header after the body, in case 
            # another component modified it from html context
            pageHeader.finishRenderHeader(html, head)

    def renderPageBodyOn(self, html):
        self.renderParts(html)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _title = "Page"
    def getTitle(self):
        ph = self._pageHeader
        if ph is not None:
            return ph.title
        else: return self._title
    def setTitle(self, title):
        self._title = title
        ph = self._pageHeader
        if ph is not None:
            ph.title = title
    title = property(getTitle, setTitle)

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

class WebPageHeader(HtmlBrushContextApiMixin):
    title = None
    def __init__(self, title=None):
        bctx = self._initBrushContext(None)
        self._parts = bctx.pushBrush(bctx.head())

        self.title = title
        self._references = set()

    def copy(self):
        r = self.__class__(self.title)
        r._references = self._references.copy()
        self._parts.copyElementsTo(r._parts)
        return r

    def hasReference(self, ref):
        return ref in self._references
    def addReference(self, ref):
        allRefs = self._references
        if ref not in allRefs:
            allRefs.add(ref)
            return True
        else:
            return False

    def link(self, href, rel, type):
        """Adds a link to the header if it has not already been added"""
        if self.addReference(href):
            return self['link'](
               href=href, rel=rel, type=type)

    def stylesheet(self, href, rel='stylesheet'):
        """Links a stylesheet to the page header"""
        return self.link(href, rel, 'text/css')
    css = stylesheet

    def script(self, *args, **kw):
        kw.setdefault('type', "text/javascript")
        return self['script'](*args, **kw)

    def javascript(self, src_url, **kw):
        if self.addReference(src_url):
            kw['src'] = src_url
            kw.setdefault('type', "text/javascript")
            return self['script']('', **kw)
    js = javascript

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def startRenderHeader(self, html):
        html.pageHeader = self
        return html.head()

    def finishRenderHeader(self, html, head):
        with head:
            if self.title is not None:
                html.title(self.title)
            self._parts.copyElementsTo(head)

