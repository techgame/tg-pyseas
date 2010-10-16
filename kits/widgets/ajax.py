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

from contextlib import contextmanager
from pyseas.component import WebComponentBase, WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AjaxResponse(WebComponentBase):
    def __init__(self, tgtMap, tgtResponse):
        self.tgtMap = tgtMap
        self.tgtResponse = tgtResponse

    def renderHtmlOn(self, html):
        self.tgtMap.installInCtx(html)
        res = self.tgtResponse
        if res is not None:
            html.ctx['ajaxTarget'] = res
            html.render(res)
        else: html.raw('')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AjaxComponentDispatch(object):
    fmtAjaxTargetJS = '''
        var ctxUrl = ctxUrl || {{}};
        ctxUrl["{key}"] = "{url}";
    '''
    key = 'oid'

    def __init__(self, html, key=None):
        if key is not None:
            self.key = key

        self.db = {}
        self.url = html.callback(self.ajaxAction, True)

        js = self.fmtAjaxTargetJS.format(key=self.key, url=self.url)
        if html.ctx.pageHeader is not None:
            html.ctx.pageHeader.script(js)
        else: html.script(js)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def fromContext(klass, html, key=None):
        self = html.ctx.get((klass, key))
        if self is None:
            self = klass(html, key)
            self.installInCtx(html)
        return self

    @classmethod
    @contextmanager
    def renderCtxHtmlOn(klass, html, tgt):
        self = klass.fromContext(html, klass.key)
        oid = self.addTarget(html, tgt)
        if oid is None:
            yield
            return

        with html.div(id=oid, class_=self.key):
            yield

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def installInCtx(self, html):
        html.ctx[(self.__class__, self.key)] = self

    def addTarget(self, html, tgt, oid=None):
        # assure the target has an ajaxAction
        tgt.ajaxAction

        if tgt is html.ctx.get('ajaxTarget'):
            # we're the target of an AjaxResponse, return sentinal
            return None

        if oid is None:
            oid = '%s-%s'%(self.key, len(self.db))
        self.db[oid] = tgt
        return oid

    def ajaxAction(self, kwargs):
        kwargs = dict(kwargs.iteritems())
        kwargs.pop('!')
        oid = kwargs.pop('!x')
        tgt = self.db[oid]
        if tgt is None:
            return AjaxResponse(self, None)

        res = tgt.ajaxAction(oid, None, kwargs)
        if not getattr(res, 'isWebComponent', bool)():
            res = tgt.itemAsComponent(res)

        if hasattr(res, 'ajaxAction'):
            self.db[oid] = res
        return AjaxResponse(self, res)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def ajaxContext(): 
    return AjaxComponentDispatch

class AjaxWebComponent(WebComponent):
    ctxDecorators = [ajaxContext()]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

jsAjaxUtilities = '''
function ctxJoin(key, args) {
  var E = encodeURIComponent;
  var r = [ctxUrl[key.split('-')[0]], "!x="+E(key)];
  if (args) for (var k in args) r.push(E(k)+"="+E(args[k]))
  return r.join("&")
}
'''

