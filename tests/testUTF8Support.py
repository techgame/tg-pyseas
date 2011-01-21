# -*- coding: utf-8 -*- vim: set ts=4 sw=4 expandtab:
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
import codecs
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def testHtmlUtfEncoding():
    wrc = WebRenderContext(None, None)
    html = wrc.createRenderer()

    with html.div():
        html.p(u'Université du Québec & Ontario')

    r = html.result()
    assert r == '<div><p>Universit\xc3\xa9 du Qu\xc3\xa9bec &amp; Ontario</p></div>'

def testHtmlUtfUrl():
    wrc = WebRenderContext(None, None)
    html = wrc.createRenderer()

    url = html.url('', host=u'Université du Québec & Ontario')
    assert url == '?host=Universit%C3%A9%20du%20Qu%C3%A9bec%20%26%20Ontario'

def testFlaskRoundTrip():
    from flask import Flask, request, jsonify
    app = Flask('app')
    @app.route('/')
    def test():
        host = request.args['host']
        assert host == u'Université du Québec & Ontario'
        return jsonify(host=host)
    app = app.test_client()

    wrc = WebRenderContext(None, None)
    html = wrc.createRenderer()

    url = html.url('', host=u'Université du Québec & Ontario')
    rv = app.get(url)

