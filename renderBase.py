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
from .utils import objectmethod

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebCallbackMap(object):
    fmtUrl = '/cb/{0}?cid={1}'
    def __init__(self, fmtUrl=None):
        self.db = defaultdict(dict)
        if fmtUrl is not None:
            self.fmtUrl = fmtUrl

    def addUrlEntry(self, rid, cid, callback, context=None):
        self.db[rid][cid] = callback, context
        url = self.fmtUrl.format(rid, cid)
        return url
    add = addUrlEntry

    def find(self, rid, cid):
        rid = int(rid); cid = int(cid)
        return self.db[rid][cid]

    def callback(self, rid, cid):
        callback, context = self.find(rid, cid)
        return callback(), context

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebRendererBase(object):
    context = None
    cbMap = WebCallbackMap()

    def __init__(self, context=None, cbMap=None):
        self.context = context
        if cbMap is not None:
            self.cbMap = cbMap

    def render(self, root, **kw):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def composedRenderOn(self, target):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def urlCB(self, callback, context=None):
        if not callable(callback):
            raise ValueError("Expected a callable object")

        rid = abs(id(self.root))
        if hasattr(callback, 'im_func'):
            cid = hash((callback.im_func, callback.im_self))
        else: cid = id(callback)
        cid = abs(cid)

        if context is None:
            context = self.context
        return self.cbMap.add(rid,cid, callback, context)

    @objectmethod
    def callback(meOrMyKind, rid, cid):
        return meOrMyKind.cbMap.callback(rid, cid)

