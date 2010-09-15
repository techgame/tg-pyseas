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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

componentAdaptorMap = {}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def adaptItemAsComponent(item, default=NotImplemented, adaptorMap=componentAdaptorMap):
    if getattr(item, 'isWebComponent', bool)():
        return item

    asWebComponent = getattr(item, 'asWebComponent', None)
    if asWebComponent:
        return asWebComponent()

    key = getattr(item, 'wcAdaptorKey', None)
    adaptor = adaptorMap.get(key)
    if adaptor is not None:
        return adaptor(item)

    if callable(item):
        adaptor = adaptorMap.get(callable)
        if adaptor is not None:
            return adaptor(item)

    for key in type(item).mro():
        adaptor = adaptorMap.get(key)
        if adaptor is not None:
            return adaptor(item)

    if default is NotImplemented:
        raise ValueError("Expected item to be a WebComponent or callable")
    else: return default

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def registerAdaptor(adaptor, keys, adaptorMap=componentAdaptorMap):
    res = dict.fromkeys(keys, adaptor)
    adaptorMap.update(res)
    return res

