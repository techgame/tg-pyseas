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

import uuid
import urlparse
import urllib

import flask

from .renderBase import WebCallbackMap
from .renderElementMaker import WebRenderer

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ComponentSession(object):
    WebCallbackMap = WebCallbackMap
    WebRenderer = WebRenderer
    redirect = staticmethod(flask.redirect)

    def __init__(self, mgr):
        self.root = mgr.RootFactory()
        self.cbMap = self.WebCallbackMap(mgr.url)

    def callback(self):
        url = self.cbMap.callback(flask.request.args)
        if url: return self.redirect(url)

    def perform(self, component, **kw):
        r = self.callback()
        if r is not None: 
            return r

        if callable(component):
            component = component(self.root)
        if component is not None:
            wr = self.bindRenderer(kw.pop('decorators', []))
            return wr.render(component, **kw)
    __call__ = perform

    def bindRenderer(self, decorators=[]):
        wr = self.WebRenderer(self.cbMap)
        wr.decorators.extend(decorators)
        #from . import halos
        #wr.decorators.append(halos.Halo())
        return wr

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ComponentSessionManager(object):
    ComponentSession = ComponentSession
    session = flask.session

    key = property(lambda self: self.__class__.__name__)


    def __init__(self, RootFactory, url):
        self.componentSessionDb = {}
        self.RootFactory = RootFactory
        self.url = url

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def lookup(self, orCreate=True):
        entryKey = self.session.get(self.key)
        if entryKey is not None:
            entry = self.componentSessionDb.get(entryKey)
            if entry is None:
                entryKey = None
        else: entry = None

        if entryKey is None and orCreate:
            entry = self.ComponentSession(self)
            entryKey = id(entry)
            self.componentSessionDb[entryKey] = entry
            self.session[self.key] = entryKey
        return entry

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def urljoin(self, path=None, **kw):
        if not path: return self.url
        if not isinstance(path, basestring):
            path = '/'.join(str(e) for e in path)

        if kw: path += '?'+urllib.urlencode(kw)
        return urlparse.urljoin(self.url, path)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def callback(self):
        cs = self.lookup(False)
        if cs is not None:
            return cs.callback()

    def perform(self, component, **kw):
        cs = self.lookup(True)
        return cs.perform(component, **kw)

