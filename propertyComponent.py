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
from types import FunctionType
from .component import WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PropertyComponentBase(WebComponent):
    def __init__(self, hostObject):
        pass

    def initFromComponentSlot(self, slot):
        pass

    @classmethod
    def property(klass, *args, **kw):
        return ComponentSlot(klass, *args, **kw)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PropertyComponent(PropertyComponentBase):
    state = None

    def __init__(self, hostObject):
        self._host = weakref.ref(hostObject)

    def initFromComponentSlot(self, slot):
        self._methodMap = slot.methodMap

    def currentRenderMethod(self):
        mm = self._methodMap
        return mm.get(self.state) or mm.get(None)

    def invokeCurrent(self, *args, **kw):
        host = self._host()
        renderFn = self.currentRenderMethod()
        return renderFn(host, *args, **kw)
    __call__ = invokeCurrent

    def renderHtmlOn(self, html):
        return self.invokeCurrent(html)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ComponentSlot(object):
    factory = PropertyComponent

    publicName = None
    privateName = None
    fmtPrivateName = '__wcslot_%s'

    def __init__(self, factory=None, *args, **kw):
        self.methodMap = {}
        if args or kw:
            factory = partial(factory, *args, **kw)
        if factory is not None:
            self.factory = factory

    def copy(self):
        return self.branch(self.factory)
    def branch(self, factory, *args, **kw):
        cpy = self.__class__(factory, *args, **kw)
        cpy.methodMap.update(self.methodMap)
        return cpy

    def createSlotItem(self, obj):
        item = self.factory(obj)
        self.initSlotItem(item)
        return item

    def initSlotItem(self, item):
        init = getattr(item, 'initFromComponentSlot', None)
        if init is not None:
            init(self)

    def method(self, state=None):
        """Bind a method for state for the property component's render method"""
        if isinstance(state, FunctionType):
            self.methodMap[None] = state
            return state

        def decorator(fn):
            self.methodMap[state] = fn
            return fn
        return decorator

    #~ property protocol ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __get__(self, obj, klass):
        attrName = self.privateName or self.findSlotName(klass)
        if obj is None:
            return self

        item = getattr(obj, attrName, None)
        if item is None:
            item = self.createSlotItem(obj)
            setattr(obj, attrName, item)
        return item

    def __set__(self, obj, item):
        attrName = self.privateName or self.findSlotName(type(obj))
        setattr(obj, attrName, item)

    def __delete__(self, obj):
        attrName = self.privateName or self.findSlotName(type(obj))
        delattr(obj, attrName)

    #~ utilities ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def findSlotName(self, klass):
        """Return the name of the property object on the class"""
        for k,v in vars(klass).iteritems():
            if v is self:
                self.publicName = k
                self.privateName = self.fmtPrivateName % (k,)
                return k
        raise LookupError("Name for component not found")

