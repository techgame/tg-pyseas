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

import time
from functools import partial

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def generationId(d=300, m=60*60*19*31):
    return int((time.time() % m)/d)

class WebCallbackRegistry(object):
    url = ''
    fmtUrl = '{0}?!={1}'

    def __init__(self, url=None, fmtUrl=None):
        self.gen0 = self.newGenerationId()
        self.gen = self.gen0-1
        self.clear()

        if url is not None:
            self.url = url
        if fmtUrl is not None:
            fmtUrl.format(self.url, 'rid')
            self.fmtUrl = fmtUrl

    def newGenerationId(self):
        return 1024*generationId()

    def addCallback(self, callback, addRequestArgs=False):
        if not callable(callback):
            raise ValueError("Expected a callable object")

        cid = self.dbKeyForCallback(callback)
        cbUrl = self.fmtUrl.format(self.url, cid)
        self.db[cid] = callback, addRequestArgs
        return cbUrl
    add = addCallback

    def dbKeyForCallback(self, callback):
        if not callable(callback):
            raise ValueError("Expected a callable object")

        if hasattr(callback, 'im_func'):
            cbKey = hash((callback.im_func, callback.im_self))
        else: cbKey = id(callback)

        return self.ciNext(cbKey)

    _cidx = 0
    def ciNext(self, cbKey):
        ci = self.db.get(cbKey)
        if ci is None:
            ci = self._cidx
            self._cidx = ci+1
            ci = '%x.%x'%(self.gen, ci)
            self.db[cbKey] = ci
        return ci

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clear(self):
        self.gen += 1
        self.db = {}
        self.shared = {}

    def find(self, kwargs, default=False):
        cid = kwargs.get('!')
        if cid is None:
            return None
        cb, addArgs = self.db.get(cid, (default, False))
        if addArgs:
            cb = partial(cb, kwargs)
        return cb
    
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

