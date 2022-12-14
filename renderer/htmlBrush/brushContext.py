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

import weakref
from functools import partial

from .brushes import htmlTagBrushMap
from .brushAttrs import HtmlBrushAttrs
from .urlTools import UrlToolsMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CallbackRegistryMixin(UrlToolsMixin):
    #~ callback registry accessors ~~~~~~~~~~~~~~~~~~~~~~

    def bind(self, callback, *args, **kw):
        if args or kw:
            callback = partial(callback, *args, **kw)
        return self.callbackUrl(callback)

    def callbackUrl(self, callback, addRequestArgs=False):
        return self._cbRegistry.addCallback(callback, addRequestArgs)
    callback = callbackUrl

    def callbackUrlAttrs(self, callback, **tagAttrs):
        attrs = {}
        # get attrs from decorated functions
        func = getattr(callback, 'func', callback)
        attrs.update(getattr(callback, 'attrs', []))

        if tagAttrs: attrs.update(tagAttrs)

        url = self.callback(callback)
        return url, attrs

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NullContextManager(object):
    def __enter__(self): pass
    def __exit__(self, *args): pass

class HtmlBrushContext(CallbackRegistryMixin):
    tagBrushMap = htmlTagBrushMap

    def __init__(self, cbRegistry, tagBrushMap=None):
        self._initBrushContext(cbRegistry, tagBrushMap)

    def _initBrushContext(self, cbRegistry, tagBrushMap=None):
        self._wr = weakref.ref(self)
        self._brushStack = []
        self._cbRegistry = cbRegistry
        if tagBrushMap is not None:
            self.tagBrushMap = tagBrushMap

    #~ brush binding and creation ~~~~~~~~~~~~~~~~~~~~~~~

    def bindBrush(self, tag):
        brush = self.tagBrushMap.get(tag)
        if brush is None:
            raise LookupError("Brush %r not found"%(tag,), tag)
        return partial(brush, self._wr, tag)

    def createBrush(self, tag, *args, **kw):
        brush = self.bindBrush(tag)
        return brush(*args, **kw)

    def inBrushRenderCtx(self, obj):
        top = self.topBrush(False)
        if top is None:
            return NullContextManager()
        return top.inBrushRenderCtx(obj)

    #~ brush context stack ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _currentBrush = None
    def topBrush(self, orLast=True):
        stack = self._brushStack
        if stack: return stack[-1]
        if orLast:
            return self._currentBrush

    def pushBrush(self, brush=None):
        self._brushStack.append(brush)
        return brush

    def popBrush(self):
        brush = self._brushStack.pop()
        self._currentBrush = brush
        return brush

    def onBrushCreated(self, brush):
        tb = self.topBrush(False)
        if tb is not None:
            tb.addImplicitBrush(brush)
        self._currentBrush = brush
        return tb

    #~ results ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __html__(self):
        return self.topBrush(True).__html__()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Brush context with getattr/getitem and call
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlBrushContextApiImpl(object):
    def __getitem__(self, tag):
        return self.bindBrush(tag)

    def __call__(self, tag, *args, **kw):
        brush = self.bindBrush(tag)
        return brush(*args, **kw)

    def __getattr__(self, tag):
        if not tag.startswith('_'):
            try:
                return self.bindBrush(tag)
            except LookupError, err:
                raise AttributeError(*err.args)

        else: raise AttributeError(tag)

    def __str__(self): 
        return str(self.__html__())
    def __unicode__(self): 
        return unicode(self.__html__())

    @staticmethod
    def attrs(class_=None, style=None, **attrs):
        attrs = HtmlBrushAttrs(attrs)
        if class_ is not None:
            attrs['class'] = class_
        if style is not None:
            attrs['style'] = style
        return attrs

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlBrushContextApi(HtmlBrushContextApiImpl, HtmlBrushContext):
    pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlBrushContextApiMixin(HtmlBrushContextApiImpl, CallbackRegistryMixin):
    _brushCtx = None

    def _initBrushContext(self, cbRegistry, tagBrushMap=None):
        self._cbRegistry = cbRegistry
        self._brushCtx = HtmlBrushContextApi(cbRegistry, tagBrushMap)
        self.bindBrush = self._brushCtx.bindBrush
        self.createBrush = self._brushCtx.createBrush
        return self._brushCtx

    def bindBrush(self, tag):
        return self._brushCtx.bindBrush(tag)
    def createBrush(self, tag, *args, **kw):
        return self._brushCtx.createBrush(tag, *args, **kw)

    def topBrush(self, orLast=True):
        return self._brushCtx.topBrush(orLast)
    def addBrush(self, brush):
        return self.topBrush().addBrush(brush)
    def addItem(self, item):
        return self.topBrush().addItem(item)
    def addAttrs(self, attrs):
        return self.topBrush().addAttrs(attrs)

