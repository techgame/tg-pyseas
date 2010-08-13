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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebRendererBase(object):
    cbMap = defaultdict(dict)
    context = None

    def __init__(self, context=None, fmtUrl=None):
        self.context = context
        if fmtUrl is not None:
            self.fmtUrl = fmtUrl

    def render(self, root, pretty_print=True):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def urlCB(self, cb, context=None):
        rid = abs(id(self.root))
        if hasattr(cb, 'im_func'):
            cid = hash((cb.im_func, cb.im_self))
        else: cid = id(cb)
        cid = abs(cid)
        if context is None:
            context = self.context
        self.cbMap[rid][cid] = (cb, context)
        return self.asUrlCB(rid, cid)

    fmtUrl = '/cb/{0}/{1}'
    def asUrlCB(self, rid, cid):
        return self.fmtUrl.format(rid, cid)

    @classmethod
    def findCB(klass, rid, cid):
        return klass.cbMap[rid][cid]

    @classmethod
    def callback(klass, rid, cid):
        cb, context = klass.findCB(rid, cid)
        cb()
        return context

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _decorators = None
    def getDecorators(self):
        r = self._decorators
        if r is None:
            self._decorators = r = []
        return r
    decorators = property(getDecorators)

    def renderDecoratedHTMLOn(self, target, r):
        decorators = self._decorators or ()
        for deco in decorators:
            r = deco.renderDecoratedHTMLOn(target, self, r)
        return r

    def renderHTMLAfterOn(self, E, r):
        return r

