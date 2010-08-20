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
import urlparse
import urllib

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebCallbackMap(object):
    url = ''
    fmtUrl = '{0}?ci={1}'

    def __init__(self, url=None, fmtUrl=None):
        self.db = {}
        if url is not None:
            self.url = url
        if fmtUrl is not None:
            fmtUrl.format(self.url, 'rid')
            self.fmtUrl = fmtUrl

    def addUrlEntry(self, callback, context=None):
        if not callable(callback):
            raise ValueError("Expected a callable object")

        cid = self.dbKeysForCallback(callback)
        url = self.fmtUrl.format(self.url, cid)
        self.db[cid] = callback, context
        return url
    add = addUrlEntry

    def dbKeysForCallback(self, callback):
        if not callable(callback):
            raise ValueError("Expected a callable object")

        if hasattr(callback, 'im_func'):
            cid = hash((callback.im_func, callback.im_self))
        else: cid = id(callback)

        return str(abs(cid))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clear(self):
        self.db.clear()

    def find(self, cid):
        return self.db[cid]

    def kwFind(self, kwargs):
        cid = kwargs.get('ci')
        if cid is not None:
            return self.find(cid)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def callback(self, kwargs):
        r = self.callbackEx(kwargs)
        if r: r = r[1]
        return r
    def callbackEx(self, kwargs):
        """If a callback is run, returns result of callback and url"""
        try:
            entry = self.kwFind(kwargs)
            if entry is None:
                return False
        except LookupError as err:
            return self.postLookupError()

        callback, context = entry
        res = callback()
        return self.postCallback(res, context)
    
    def postLookupError(self):
        return None, self.url
    def postCallback(self, res, context):
        return res, self.urljoin(context)

    #~ utility methods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def urljoin(self, path=None, **kw):
        if not path: return self.url
        if not isinstance(path, basestring):
            path = '/'.join(str(e) for e in path)

        if kw: path += '?'+urllib.urlencode(kw)
        return urlparse.urljoin(self.url, path)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Utility mixin
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CallbackRegistrationMixin(object):
    #~ callback registry methods ~~~~~~~~~~~~~~~~~~~~~~~~

    def bind(self, callback, *args, **kw):
        return self.ctxBindEx(None, callback, args, kw)
    def ctxBind(self, context, callback, *args, **kw):
        return self.ctxBindEx(context, callback, args, kw)
    def ctxBindEx(self, context, callback, args, kw):
        if args or kw:
            callback = functools.partial(callback, *args, **kw)
        return self.callback(callback, context)
    def callback(self, callback, context=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

