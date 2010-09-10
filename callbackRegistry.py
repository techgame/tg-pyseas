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

def missingCallback():
    pass

class WebCallbackRegistry(object):
    url = ''
    fmtUrl = '{0}?ci={1}'

    def __init__(self, url=None, fmtUrl=None):
        self.db = {}
        if url is not None:
            self.url = url
        if fmtUrl is not None:
            fmtUrl.format(self.url, 'rid')
            self.fmtUrl = fmtUrl

    def addCallback(self, callback):
        if not callable(callback):
            raise ValueError("Expected a callable object")

        cid = self.dbKeyForCallback(callback)
        cbUrl = self.fmtUrl.format(self.url, cid)
        self.db[cid] = callback
        return cbUrl
    add = addCallback

    def dbKeyForCallback(self, callback):
        if not callable(callback):
            raise ValueError("Expected a callable object")

        if hasattr(callback, 'im_func'):
            cid = hash((callback.im_func, callback.im_self))
        else: cid = id(callback)

        return str(abs(cid))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clear(self):
        self.db.clear()

    def find(self, kwargs, default=missingCallback):
        cid = kwargs.get('ci')
        if cid is None:
            return None
        return self.db.get(cid, default)
    
    def callback(self, kwargs):
        callback = self.find(kwargs)
        return callback()

    @classmethod
    def newRegistryMap(klass):
        return WebCallbackRegistryMap(klass)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebCallbackRegistryMap(dict):
    Registry = WebCallbackRegistry

    def __init__(self, Registry=None):
        if Registry is not None:
            self.Registry = Registry

    def __missing__(self, url):
        r = self.Registry(url)
        self[url] = r
        return r

    def __call__(self, url):
        return self[url]

