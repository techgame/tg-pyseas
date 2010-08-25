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

from pyseas import WebRenderContext

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def testHtmlRenderer():
    wrc = WebRenderContext(None)
    html = wrc.createRenderer()

    with html.div():
        html.p('a paragraph using', html.strong('both'), 
                'implicit and explicit', html.i('tags'))
        html.a('link')

    r = html.result()
    assert r == (
        '<div><p>a paragraph using<strong>both</strong>'
        'implicit and explicit<i>tags</i></p><a>link</a></div>'), r

def testHtmlEmptyDiv():
    wrc = WebRenderContext(None)
    html = wrc.createRenderer()
    with html.div(): pass

    r = html.result()
    print r
    assert r == ('<div></div>')

