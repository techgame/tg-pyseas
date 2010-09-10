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

from functools import partial, update_wrapper

import flask

from pyseas.context import WebViewContextBase

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FlaskWebViewContextBase(WebViewContextBase):
    #~ Dispatch request composed method ~~~~~~~~~~~~~~~~~

    def dispatchRequest(self, request=flask.request, **nsCtx):
        return self._performDispatch(request, nsCtx)

    #~ Render dispatch extension points ~~~~~~~~~~~~~~~~~

    def _renderCallbackMissing(self, request):
        if request.is_xhr:
            return flask.abort(404)
        return flask.redirect(request.path)
    def _renderCallbackRedirect(self, request):
        return flask.redirect(request.path)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FlaskWebViewContext(FlaskWebViewContextBase):
    def __init__(self, appOrModel):
        self._appOrModel = appOrModel
        self._views = {}
        self._initViewContext()

    def route(self, rule, **options):
        routeDecorator = self._appOrModel.route(rule, **options)
        def asComponentView(view):
            viewFn = partial(self._componentView, view)
            viewFn = update_wrapper(viewFn, view)
            return routeDecorator(viewFn)
        return asComponentView

    def _componentView(self, view, *args, **kw):
        rootViewFn = partial(view, *args, **kw)
        return self.dispatchRequest(rootViewFn=rootViewFn)

    def findRootForRequest(self, request, nsCtx):
        rootViewFn = nsCtx['rootViewFn']
        return rootViewFn()

