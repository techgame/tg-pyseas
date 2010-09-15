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

from pyseas import WebListComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def addMenuItem(self, *args, **kw):
    Factory = getattr(self, 'MenuItem', type(self))
    return self.add(Factory(*args, **kw))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MenuItem(WebListComponent):
    stateAttrs = [None, {'class': 'active'}]

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def isMenuItem(self):
        return True

    addMenuItem = addMenuItem
    addItem = addMenuItem

    def renderHtmlOn(self, html):
        attrs = self.stateAttrs[self in html.ctx.selected]
        with html.li(attrs):
            self.renderMenuItem(html)
            if self.parts:
                self.renderSubMenu(html)

    def renderMenuItem(self, html):
        html.a(self.name, href=self.url)

    def renderSubMenu(self, html):
        with html.ul():
            self.renderParts(html)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Menu(WebListComponent):
    cssClass = 'menu'
    MenuItem = MenuItem

    addMenuItem = addMenuItem
    addItem = addMenuItem

    def renderHtmlOn(self, html):
        item = self.findSelectedMenuItem(html.ctx.request.path)
        html.ctx.selected.add(item)

        with html.ul(class_=self.cssClass):
            self.renderParts(html)

    def iterMenuItems(self, nested=False):
        partQ = list(self.parts)
        for mi in partQ:
            if getattr(mi, 'isMenuItem', bool)():
                yield mi
                if nested:
                    partQ.extend(mi.parts)

    def findSelectedMenuItem(self, path):
        url = ''; r = None
        for menuItem in self.iterMenuItems():
            itemUrl = menuItem.url
            if len(url)<len(itemUrl) and path.startswith(itemUrl):
                url = itemUrl
                r = menuItem
        return r

