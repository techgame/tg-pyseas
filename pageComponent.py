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

from .component import WebComponentBase
from .listComponent import WebListPartsMixin

from .renderer.htmlBrush import HtmlBrushContextApiMixin
from .renderer.htmlBrush import htmlHeadTagBrushMap

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

        self.init()

    def init(self):
        pass

    def renderOn(self, rctx):
        return rctx.renderPage(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def renderHtmlOn(self, html):
        pageHeader = self.pageHeader.copy()
        with html.document():
            html.doctype()
            with html.html():
                head = pageHeader.startRenderHeader(html)

                self.renderPageHeaderOn(pageHeader)
                with html.body():
                    self.renderPageBodyOn(html)

                # render the header after the body, in case 
                # another component modified it from html context
                pageHeader.finishRenderHeader(html, head)

    def renderPageHeaderOn(self, pageHeader):
        pass
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
        pageHeader = self._pageHeader
        if pageHeader is None:
            pageHeader = WebPageHeader(self.title)
            self._pageHeader = pageHeader
            self.initPageHeader(pageHeader)
        return pageHeader
    pageHeader = property(getPageHeader)

    def initPageHeader(self, pageHeader):
        pass


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Page Header
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebPageHeader(HtmlBrushContextApiMixin):
    htmlHeadTagBrushMap = htmlHeadTagBrushMap
    title = None

    def __init__(self, title=None):
        bctx = self._initBrushContext(None, self.htmlHeadTagBrushMap)
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
        html.ctx.pageHeader = self
        return html.head()

    def finishRenderHeader(self, html, head):
        with head:
            if self.title is not None:
                html.title(self.title)
            self._parts.copyElementsTo(head)

