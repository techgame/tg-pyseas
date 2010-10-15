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

from pyseas.renderer import WebRenderContext

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

resA = '<div id=A1></div><div id=A2></div>'
resB = '<div id=B1></div><div id=B2></div>'
resAB = '<div id=A1></div>'+resB+'<div id=A2></div>'
resBodyA = '<body>'+resA+'</body>'
resBodyAB = '<body>'+resAB+'</body>'
resBodyOnly = '<body></body>'

def assertEqual(a,b): assert a == b, (a,b)

def makeTestData(addA=False, addB=False):
    wrc = WebRenderContext(None, None)
    html = wrc.createRenderer()

    with html.body():
        with html.isolated() as A:
            html.div(id='A1')
            with html.isolated() as B:
                html.div(id='B1')
                html.div(id='B2')

            if addB: html.addBrush(B)

            html.div(id='A2')

        if addA: html.addBrush(A)

    return html, A, B

def testIsolatedHtmlBody():
    html, A, B = makeTestData(False, False)
    assertEqual(B.__html__(), resB)
    assertEqual(A.__html__(), resA)
    assertEqual(html.result(), resBodyOnly)

def testIsolatedAddA():
    html, A, B = makeTestData(True, False)

    assertEqual(B.__html__(), resB)
    assertEqual(A.__html__(), resA)
    assertEqual(html.result(), resBodyA)

def testIsolatedAddB():
    html, A, B = makeTestData(False, True)

    assertEqual(B.__html__(), resB)
    assertEqual(A.__html__(), resAB)
    assertEqual(html.result(), resBodyOnly)

def testIsolatedHtmlToAtoB():
    html, A, B = makeTestData(True, True)

    assertEqual(B.__html__(), resB)
    assertEqual(A.__html__(), resAB)
    assertEqual(html.result(), resBodyAB)

