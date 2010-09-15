# -*- coding: utf-8 -*-
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

from pyseas import WebComponent, WebListComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TabPage(WebListComponent):
    title = 'Tab Page'
    body = 'Tab Body'
    cssClass = ''

    def __init__(self, title=None, body=None, cssClass=None):
        if title is not None:
            self.title = title
        if body is not None:
            self.body = body
        if cssClass is not None:
            self.cssClass = cssClass

    def renderTab(self, html, isActive, setSelected):
        with html.a(class_=isActive and 'active') as a:
            a.bind(setSelected, self)
            html.autoRender(self.title)

    def renderHtmlOn(self, html):
        with html.div(class_=self.cssClass):
            html.autoRender(self.body)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TabPageset(WebListComponent):
    TabPage = TabPage
    cssClass = 'tabs'
    tabClass = ''
    tabItemClass = ''

    def addPage(self, *args, **kw):
        page = self.TabPage(*args, **kw)
        self.add(page)
        return page

    _currentTab = None
    def selectTab(self, tabItem):
        if tabItem not in self.parts:
            raise ValueError("Selected tab item not in collection")
        self._currentTab = tabItem

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def renderHtmlOn(self, html):
        current = self._currentTab
        if current is None:
            current = self.parts[0]

        with html.div(class_=self.cssClass):
            self.renderHead(html, current)
            self.renderBody(html, current)

    def renderHead(self, html, current):
        with html.ul(class_=self.tabClass):
            for part in self.parts:
                with html.li(class_=self.tabItemClass):
                    part.renderTab(html, part is current, self.selectTab)

    def renderBody(self, html, current):
        html.render(current)

