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

from functools import partial
from contextlib import contextmanager

from .adaptor import AdaptableMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebComponentBase(object):
    def isWebComponent(self):
        return True

    def render(self, outputKey='html', cbRegistry=None):
        from pyseas.renderer import WebRenderContext
        rctx = WebRenderContext(cbRegistry, outputKey)
        return rctx.render(self)

    def renderOn(self, rctx):
        return rctx.renderComponent(self)

    @contextmanager
    def renderCtxOn(self, v, outer):
        yield

    def renderHtmlOn(self, html):
        # provide a reasonable default to aid debugging
        html.div(repr(self))

class WebComponentContextBase(object):
    def isWebComponent(self):
        return False

    @contextmanager
    def renderCtxHtmlOn(self, html, tgt):
        yield

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AnswerableMixin(object):
    def isAnswerable(self):
        return self._answerCallInfo is not None
    def answer(self, *args, **kw):
        answerTgt, onAnswer = self._answerCallInfo
        del self._answerCallInfo
        answerTgt.popTarget()
        onAnswer(*args, **kw)
        return answerTgt

    _answerCallInfo = None
    def asCalledOn(self, answerTgt, onAnswer):
        self._answerCallInfo = (answerTgt, onAnswer)
        return self
    def getAnswerTarget(self):
        return self._answerCallInfo[0]
    answerTarget = property(getAnswerTarget)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebComponent(WebComponentBase, AnswerableMixin, AdaptableMixin):
    def renderOn(self, rctx):
        target = self.target
        if target is not None:
            return target.renderOn(rctx)
        else:
            return rctx.renderComponent(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getTarget(self):
        ts = self.targetStack
        if ts: return ts[-1]
    target = property(getTarget)

    targetStack = None
    def pushTarget(self, target):
        ts = self.targetStack
        if ts is None:
            self.targetStack = ts = []
        ts.append(target)
        return target
    def popTarget(self):
        return self.targetStack.pop()

    @contextmanager
    def pealTarget(self, idx=-1):
        ts = self.targetStack
        tsSave = ts[idx:]
        del ts[idx:]
        try: 
            yield
        finally:
            ts.extend(tsSave)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @contextmanager
    def renderCtxOn(self, v, outer):
        with v.renderNestedCtx(self, outer, self.ctxDecorators):
            yield

    ctxDecorators = []
    def addCtxDecorators(self, aCtxObj):
        r = self.__dict__.get('ctxDecorators')
        if r is None:
            # create an instance copy
            r = list(self.ctxDecorators or [])
            self.ctxDecorators = r
        r.append(aCtxObj)
        return aCtxObj

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _targetStack = None
    def call(self, callItem, onAnswer=None):
        if onAnswer is None:
            onAnswer = self.onAnswer
        elif isinstance(onAnswer, basestring):
            attrName = onAnswer
            onAnswer = lambda value:(setattr, attrName, value)

        asCalledOn = getattr(callItem, 'asCalledOn', None)
        if asCalledOn is None:
            pxy = self.itemAsComponent(callItem)
            asCalledOn = pxy.asCalledOn

        target = asCalledOn(self, onAnswer)
        if target is not None:
            return self.pushTarget(target)

    answered = NotImplemented
    def onAnswer(self, value=None):
        self.answered = value

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebProxyComponent(WebComponent):
    def __init__(self, item):
        self._proxyItem_ = item

    def renderHtmlOn(self, html):
        return self._proxyItem_(html)

    def __call__(self, *args, **kw):
        return self._proxyItem_(*args, **kw)

    def __getattr__(self, name):
        if name.startswith('render'):
            return self._proxyItem_
        return super(WebProxyComponent, self).__getattr__(name)

WebProxyComponent.registerAsAdaptorFor(callable)

