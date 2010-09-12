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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebComponent(WebComponentBase):
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
        with v.renderNestedCtx(self, outer, self._ctxDecorators):
            yield

    _ctxDecorators = None
    def getCtxDecorators(self):
        r = self._ctxDecorators
        if r is None:
            self._ctxDecorators = r = []
        return r
    ctxDecorators = property(getCtxDecorators)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _targetStack = None
    def call(self, item, onAnswer=None):
        if onAnswer is None:
            onAnswer = self.onAnswer
        elif isinstance(onAnswer, basestring):
            attrName = onAnswer
            onAnswer = lambda value:(setattr, attrName, value)

        item = item.asCalledOn(self, onAnswer)
        if item is not None:
            return self.pushTarget(item)

    answered = NotImplemented
    def onAnswer(self, value=None):
        self.answered = value

    _answerTarget = None
    def answer(self, *args, **kw):
        if self.target is not None:
            return self.target.answer(*args, **kw)

        answerTgt, onAnswer = self._answerTarget
        self._answerTarget = None
        answerTgt.popTarget()
        return onAnswer(*args, **kw)

    def isAnswerable(self):
        return self._answerTarget is not None

    @contextmanager
    def pealAnswer(self):
        answerTgt, onAnswer = self._answerTarget
        self._answerTarget = None
        try:
            with answerTgt.pealTarget():
                yield answerTgt
        finally:
            self._answerTarget = answerTgt, onAnswer

    def asCalledOn(self, answerTarget, onAnswer):
        self._answerTarget = (answerTarget, onAnswer)
        return self

