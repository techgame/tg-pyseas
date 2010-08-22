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

import itertools

import wtforms
from wtforms import fields, widgets, validators

from pyseas import WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WTFormComponentBase(WebComponent):
    attrErrors = {'class':'errors'}
    _fieldLabelOrders = {
        'BooleanField': -1,
        'RadioField': -1,
        'SubmitField': 0,
    }

    def renderHtmlOn(self, html):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def renderForm(self, html, form, cbPostForm, **kw):
        self.nextTabIndex = itertools.count(kw.pop('tabindex', 100)).next

        with html.form(**kw).bind(cbPostForm, form):
            for field in form:
                with html.p():
                    self.renderField(html, field)

    def renderField(self, html, field, **kw):
        if isinstance(field, basestring):
            field = getattr(self, field)

        if 'tabindex' not in kw:
            kw['tabindex'] = self.nextTabIndex()

        order = kw.get('order')
        if order is None:
            order = self._fieldLabelOrders.get(field.type, 1)

        if order > 0:
            html.raw(field.label())

        html.raw(field(**kw))

        if order < 0:
            html.raw(field.label())

        if field.errors:
            self.renderErrors(html, field.errors)

    def renderErrors(self, html, errors, **kw):
        if not errors: return
        attrs = self.attrErrors
        if kw:
            attrs = attrs.copy()
            attrs.update(kw)

        with html.ul(attrs):
            for err in errors:
                html.li(err)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WTFormComponent(wtforms.Form, WTFormComponentBase):
    def renderHtmlOn(self, html):
        self.renderForm(html, self, self.postForm)

    def postForm(self, aForm):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

