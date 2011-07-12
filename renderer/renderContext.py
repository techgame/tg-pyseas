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

from contextlib import contextmanager
from TG.pyseas.utils import IdCounters

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebRenderContext(object):
    outputKey = 'html'
    renderer = None

    def __init__(self, request, cbRegistry, outputKey=None):
        if cbRegistry is True:
            cbRegistry = self.createCallbackRegistry()
        self.cbRegistry = cbRegistry

        if outputKey is not None:
            if outputKey not in self.RenderFactoryMap:
                raise LookupError("No render factories registered for key: %r"%(outputKey,), outputKey)
            self.outputKey = outputKey

        self._initContext(request)

    #~ context utilities ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    pageHeader = None
    def _initContext(self, request):
        self.shared = getattr(self.cbRegistry, 'shared', {})
        self.db = {}
        self.request = request
        self.selected = set()
        self.idc = IdCounters()

    # mini dictonary interface
    def get(self, key, default=None):
        return self.db.get(key, default)
    def __contains__(self, key):
        return key in self.db
    def __getitem__(self, key):
        return self.db[key]
    def __setitem__(self, key, value):
        self.db[key] = value
    def __delitem__(self, key, value):
        self.db.pop(key, None)

    #~ render visitng ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def render(self, root):
        if root is None: return
        renderOn = getattr(root, 'renderOn', root)

        with self.inRenderCtx(root) as renderer:
            renderOn(self)
            return renderer.result()

    def autoRender(self, item):
        if getattr(item, 'isWebComponent', bool)():
            return self.render(item)
        else: return item

    def renderPage(self, page):
        return self.renderer._performRenderPage(page)
    def renderComponent(self, component):
        return self.renderer._performRenderComponent(component)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @contextmanager
    def inRenderCtx(self, obj=None):
        previous = self.renderer
        renderer = self.createRenderer()
        self.renderer = renderer
        yield renderer
        self.renderer = previous

    def createRenderer(self):
        factory = self.RenderFactoryMap[self.outputKey]
        return factory(self, self.cbRegistry)

    @classmethod
    def registerRenderFactory(klass, RenderFactory, *outputKeys):
        for key in outputKeys:
            klass.RenderFactoryMap[key] = RenderFactory
    RenderFactoryMap = {}


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def createCallbackRegistry(self):
        from TG.pyseas.engine import WebCallbackRegistry
        return WebCallbackRegistry()

