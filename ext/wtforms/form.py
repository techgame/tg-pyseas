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

    fieldsep = 'p'
    def renderForm(self, html, form, cbPostForm, fieldsep=None, **kw):
        if fieldsep is None:
            fieldsep = getattr(html, self.fieldsep)
        elif fieldsep is False:
            fieldsep = html.nothing

        if 'tabindex' in kw:
            self.setNextTabIndex(kw['tabindex'])

        with html.form(**kw).bind(cbPostForm, form):
            for field in form:
                with fieldsep():
                    self.renderField(html, field)

    def renderField(self, html, field, labelAttrs={}, **kw):
        if isinstance(field, basestring):
            field = getattr(self, field)

        if 'tabindex' not in kw:
            kw['tabindex'] = self.nextTabIndex()

        order = kw.get('order')
        if order is None:
            order = self._fieldLabelOrders.get(field.type, 1)

        # grab attrs for rendering
        fieldAttrs = self.attrsForField(field.name, kw)
        labelAttrs = self.attrsForFieldLabel(field.name, labelAttrs)

        if order > 0:
            html.raw(field.label(**labelAttrs))
        elif order == 0:
            if labelAttrs.get('br', False):
                html.br()

        html.raw(field(**fieldAttrs))

        if order < 0:
            html.raw(field.label(**labelAttrs))

        if field.errors:
            self.renderFieldErrors(html, field)

    def renderFieldErrors(self, html, field, **kw):
        if not field.errors: return
        attrs = self.attrErrors
        if kw:
            attrs = attrs.copy()
            attrs.update(kw)

        with html.ul(attrs):
            for err in field.errors:
                html.li(err)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    fieldAttrs = {}
    def attrsForField(self, fieldName, kwAttrs):
        attrs = self.fieldAttrs.get(fieldName, {})
        if kwAttrs:
            attrs = attrs.copy()
            attrs.update(kwAttrs)
        return attrs

    labelAttrs = {}
    def attrsForFieldLabel(self, fieldName, kwAttrs):
        attrs = self.labelAttrs.get(fieldName, {})
        if kwAttrs:
            attrs = attrs.copy()
            attrs.update(kwAttrs)
        return attrs

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _iterTabIndex = None
    def nextTabIndex(self):
        r = self._iterTabIndex
        if r is None:
            self.setNextTabIndex(100)
            r = self._iterTabIndex
        return r.next()
    def setNextTabIndex(self, nextTabIndex):
        self._iterTabIndex = itertools.count(nextTabIndex)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WTFormComponent(wtforms.Form, WTFormComponentBase):
    def renderHtmlOn(self, html):
        self.renderForm(html, self, self.postForm)

    def postForm(self, aForm):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

