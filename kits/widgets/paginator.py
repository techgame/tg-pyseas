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

from operator import itemgetter

from pyseas import WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ItemViewComponent(WebComponent):
    def __init__(self, item):
        self.item = item
    def renderHtmlOn(self, html):
        html.pre(repr(self.item))

class PaginatorBase(WebComponent):
    page = 0
    pageSize = 10
    ItemView = ItemViewComponent
    reverse = False

    def __init__(self, ItemView=None, pageSize=None, reverse=None):
        if ItemView is not None:
            self.ItemView = ItemView
        if pageSize is not None:
            self.pageSize = pageSize
        if reverse is not None:
            self.reverse = reverse

    def renderHtmlOn(self, html):
        for ea in self.pageItemViews():
            html.render(ea)

    _cacheAttrs = {}
    def clearCache(self):
        for r,v in self._cacheAttrs.items():
            setattr(self, r, v)

    def __len__(self):
        return len(self.pageItems())
    def __iter__(self):
        return self.pageItemViews()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def pageCount(self):
        pageSize = self.pageSize
        n = self.itemCount() + pageSize - 1
        return int(n / pageSize)

    def pageItems(self):
        size = self.pageSize
        p0 = self.page*size
        p1 = p0+size
        return self.itemSelection(p0, p1)

    _cacheAttrs['_itemViewMap'] = None
    _itemViewMap = None
    def pageItemViews(self):
        ivm = self._itemViewMap
        if ivm is None: 
            ivm = {}
            self._itemViewMap = ivm

        ItemView = self.ItemView
        def viewFor(e):
            r = ivm.get(e)
            if r is None:
                r = ItemView(e)
                ivm[e] = r
            return r

        r = [viewFor(e) for e in self.pageItems()]
        return r

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def hasPrevPage(self):
        return self.deltaPage(-1)[0]
    def prevPage(self):
        return self.movePage(-1)

    def hasNextPage(self):
        return self.deltaPage(+1)[0]
    def nextPage(self):
        return self.movePage(+1)

    def deltaPage(self, delta=1):
        rawPage = self.page + delta
        newPage = min(max(0, rawPage), max(0, self.pageCount()-1))
        return rawPage==newPage, newPage
    def movePage(self, delta=1):
        valid, page = self.deltaPage(delta)
        self.page = page
        return page

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def itemCount(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def itemSelection(self, p0, p1):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ListPaginator(PaginatorBase):
    def __init__(self, items, ItemView=None, **kw):
        self.items = items
        super(ListPaginator, self).__init__(ItemView, **kw)

    def itemCount(self):
        return len(self.items)

    def itemSelection(self, p0, p1):
        items = self.items
        if self.reverse:
            items = items[::-1]
        return items[p0:p1]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class DictPaginator(PaginatorBase):
    sortKey = 'key'

    def __init__(self, items, ItemView=None, **kw):
        self.items = items
        super(DictPaginator, self).__init__(ItemView, **kw)

    def itemCount(self):
        return len(self.items)

    def itemSelection(self, p0, p1):
        sortKey = self._getSortByFn()
        items = sorted(self.items.items(), key=sortKey, reverse=self.reverse)
        return map(itemgetter(1), items)

    def _getSortByFn(self):
        sortKey = self.sortKey
        if sortKey == 'key':
            sortKey = itemgetter(0)
        elif sortKey == 'value':
            sortKey = itemgetter(1)
        return sortKey

