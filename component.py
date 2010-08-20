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
    def renderOn(self, rctx):
        return rctx.renderComponent(self)

    @contextmanager
    def renderHTMLCtxOn(self, html, outer):
        yield
    def renderHTMLOn(self, html):
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

    @contextmanager
    def renderHTMLCtxOn(self, html, outer):
        with html.renderNestedCtx(self, outer, self._decorators):
            yield

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

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _decorators = None
    def getDecorators(self):
        r = self._decorators
        if r is None:
            self._decorators = r = []
        return r
    decorators = property(getDecorators)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _targetStack = None
    def call(self, item):
        item = item.asCalledOn(self.onAnwser)
        if item is not None:
            return self.pushTarget(item)

    answered = NotImplemented
    def onAnwser(self, value=None):
        self.popTarget()
        self.answered = value

    answerTarget = None
    def answer(self, value=None):
        if self.target is not None:
            return self.target.answer(value)
        else: self.answerTarget(value)
    def asCalledOn(self, answerTarget):
        self.answerTarget = answerTarget
        return self

