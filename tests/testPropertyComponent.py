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

from pyseas import WebComponent
from pyseas.propertyComponent import ComponentSlot

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TrialDelegate(WebComponent):
    def renderHtmlOn(self, html):
        html.text('delegate')

class TrialComponent(WebComponent):
    body = ComponentSlot()

    def renderHtmlOn(self, html):
        html.render(self.body)

    @body.method
    def renderBody(self, html):
        html.text('body method')

    @body.method('stateA')
    def renderBody_stateA(self, html):
        html.text('stateA method')

    @body.method('stateB')
    def renderBody_stateB(self, html):
        html.text('stateB method')

    def renderFunction(self, html):
        html.text('function')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def testComponentSlot():
    c = TrialComponent()
    assert c.render() == "body method"

def testComponentSlotTarget():
    c = TrialComponent()
    assert c.render() == "body method"

    delegate = TrialDelegate()
    c.call(delegate)
    assert c.render() == "delegate"

    delegate.answer()
    assert c.render() == "body method"

def testComponentSlotState():
    c = TrialComponent()
    assert c.render() == "body method"

    c.body.state = "stateA"
    assert c.render() == "stateA method"

    c.body.state = None
    assert c.render() == "body method"

    c.body.state = "stateB"
    assert c.render() == "stateB method"

    del c.body.state
    assert c.render() == "body method"

def testComponentSlotFunctionTarget():
    c = TrialComponent()
    assert c.render() == "body method"

    c.call(c.renderFunction)
    assert c.render() == "function"

