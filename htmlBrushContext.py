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

import functools
from .htmlBrushes import htmlTagBrushMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlBrushContextBase(object):
    tagBrushMap = htmlTagBrushMap

    def __init__(self, hostCtx, tagBrushMap=None):
        self._initBrushContext(hostCtx, tagBrushMap)

    def _initBrushContext(self, hostCtx, tagBrushMap=None):
        self._brushStack = []
        if hostCtx is not None:
            self.callbackUrlAttrs = hostCtx.callbackUrlAttrs
        if tagBrushMap is not None:
            self.tagBrushMap = tagBrushMap

    def callbackUrlAttrs(self, callback, **tagAttrs):
        raise NotImplementedError('Host Context Responsibility: %r' % (self,))

    #~ brush binding and creation ~~~~~~~~~~~~~~~~~~~~~~~

    def bindBrush(self, tag):
        brush = self.tagBrushMap.get(tag)
        if brush is None:
            raise LookupError("Brush %r not found"%(tag,), tag)
        return functools.partial(brush, self, tag)

    def createBrush(self, tag, *args, **kw):
        brush = self.bindBrush(key)
        return brush(*args, **kw)

    #~ brush context stack ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def topBrush(self):
        stack = self._brushStack
        if stack: return stack[-1]

    def pushBrush(self, brush=None):
        self._brushStack.append(brush)
        return brush

    def popBrush(self):
        brush = self._brushStack.pop()
        self._currentBrush = brush
        return brush

    _currentBrush = None
    def onBrushCreated(self, brush):
        tb = self.topBrush()
        if tb is not None:
            tb.addImplicitBrush(brush)
        self._currentBrush = brush
        return tb

    #~ results ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def resultBrush(self):
        last = self.topBrush()
        if last is None:
            last = self._currentBrush
        return last

    def resultXMLString(self, **kw):
        last = self.resultBrush()
        return last.asXMLString(**kw)

    def __html__(self):
        return self.resultBrush().__html__()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlBrushContext(HtmlBrushContextBase):
    def __getitem__(self, tag):
        return self.bindBrush(tag)

    def __call__(self, key, *args, **kw):
        brush = self.bindBrush(key)
        return brush(*args, **kw)

    def __getattr__(self, key):
        if not key.startswith('_'):
            try:
                return self.bindBrush(key)
            except LookupError, err:
                raise AttributeError(*err.args)

        else: raise AttributeError(key)

    def __str__(self): 
        return str(self.__html__)
    def __unicode__(self): 
        return unicode(self.__html__)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlBrushContextApiMixin(object):
    _brushCtx = None
    def _initBrushContext(self, hostCtx, tagBrushMap=None):
        self._brushCtx = HtmlBrushContext(hostCtx, tagBrushMap)
        return self._brushCtx

    def __getitem__(self, tag):
        return self._brushCtx.bindBrush(tag)

    def __call__(self, key, *args, **kw):
        brush = self._brushCtx.bindBrush(key)
        return brush(*args, **kw)

    def __getattr__(self, key):
        if not key.startswith('_'):
            try:
                return self._brushCtx.bindBrush(key)
            except LookupError, err:
                raise AttributeError(*err.args)

        else: raise AttributeError(key)

