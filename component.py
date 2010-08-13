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

class WebComponentBase(object):
    def render(self, context):
        return WebRenderer(context).render(self)
    def renderOn(self, E):
        return E.composedRender(self)

    def renderHTMLOn(self, E):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def renderHTMLAfterOn(self, E, r):
        return r

    def composedRenderOn(self, E):
        r = self.renderHTMLOn(E)
        if r is None: 
            raise RuntimeError("%s failed to return rendered output"%(self.__class__,))

        r = self.renderHTMLAfterOn(E, r)
        if r is None: 
            raise RuntimeError("%s failed to return rendered after output"%(self.__class__,))

        r = E.renderDecoratedHTMLOn(self, r)
        return r

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WebComponent(WebComponentBase):
    def renderOn(self, E):
        return self.target.composedRenderOn(E)

    def renderHTMLOn(self, E):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def renderHTMLAfterOn(self, E, r):
        decorators = self._decorators or ()
        for deco in decorators:
            r = deco.renderDecoratedHTMLOn(self, E, r)
        return r

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _target = None
    def getTarget(self, orSelf=True):
        r = self._target
        if r is None and orSelf:
            r = self
        return r
    def setTarget(self, target):
        self._target = target
        if target is self:
            del self._target
    target = property(getTarget, setTarget)

    _targetStack = None
    def pushTarget(self, target):
        stack = self._targetStack
        if stack is None:
            self._targetStack = stack = []

        stack.append(self._target)
        self.target = target
        return target
    def popTarget(self):
        target = self._targetStack.pop()
        self.target = target
        return target

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
        return self.target.answerTarget(value)
    def asCalledOn(self, answerTarget):
        self.answerTarget = answerTarget
        return self

