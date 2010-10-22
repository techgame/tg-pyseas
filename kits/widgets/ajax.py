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
        res = self.tgtResponse
        self.tgtMap.installInCtx(html, res)
        if res is not None:
            with html.collection():
                html.render(res)
        else: html.raw('')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AjaxContext(object):
    fmtAjaxTargetJS = 'var ctxUrl = "{url}";'

    def __init__(self, html):
        self.db = {}
        self.url = html.callback(self.ajaxDispatch, True)

        js = self.fmtAjaxTargetJS.format(url=self.url)
        if html.ctx.pageHeader is not None:
            html.ctx.pageHeader.script(js)
        else: html.script(js)

    @classmethod
    def locate(klass, html):
        self = html.ctx.get(klass)
        if self is None:
            self = klass(html)
            self.installInCtx(html)
        return self

    def installInCtx(self, html, res=None):
        html.ctx[self.__class__] = self

    def addTarget(self, key, tgt, ajaxAction):
        # assure the target has an ajaxAction
        oid = '%s-%s'%(key, len(self.db))
        self.db[oid] = (tgt, ajaxAction)
        return {'id':oid, 'class':'wc-ajax '+key}

    def __getitem__(self, index):
        get = self.db.get
        if isinstance(index, basestring):
            return get(index)[0]
        elif hasattr(index, 'items'):
            return type(index)((k,get(v)[0]) for k,v in index.items())
        else:
            return [get(v)[0] for v in index]

    def ajaxDispatch(self, kwargs):
        kwargs = dict(kwargs.iteritems())
        kwargs.pop('!', None)
        oid = kwargs.pop('!x')

        tgt, ajaxAction = self.db[oid]
        if ajaxAction is None:
            return AjaxResponse(self, None)

        res = ajaxAction(self, kwargs)
        if not getattr(res, 'isWebComponent', bool)():
            if res is not None:
                res = tgt.itemAsComponent(res, None)
            else: res = tgt

        return AjaxResponse(self, res)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AjaxWebComponent(WebComponent):
    ajaxKey = 'oid'

    def ajaxAspect(self, html, key=None, action=None):
        axc = AjaxContext.locate(html)
        if key is None:
            key = self.ajaxKey
        if action is None:
            action = self.ajaxAction
        return axc.addTarget(key, self, self.ajaxAction)

    def ajaxAction(self, axc, kwargs):
        return self

    def renderHtmlOn(self, html):
        with html.div(self.ajaxAspect(html)):
            pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

jsAjaxUtilities = '''
function ctxJoin(key, args) {
  var E = encodeURIComponent;
  var r = [ctxUrl, "!x="+E(key)];
  if (args) for (var k in args) r.push(E(k)+"="+E(args[k]))
  return r.join("&")
}
'''

