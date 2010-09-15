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
import functools

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
            callback = functools.partial(callback, *args, **kw)
        return self.callbackUrl(callback)

    def callbackUrl(self, callback):
        return self._cbRegistry.addCallback(callback)
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
        return functools.partial(brush, self._wr, tag)

    def createBrush(self, tag, *args, **kw):
        brush = self.bindBrush(tag)
        return brush(*args, **kw)

    def inBrushRenderCtx(self, obj):
        top = self.topBrush()
        if top is None:
            return NullContextManager()
        return top.inBrushRenderCtx(obj)

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
        last = self.resultBrush()
        return last.__html__()


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
        return str(self.__html__)
    def __unicode__(self): 
        return unicode(self.__html__)

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

