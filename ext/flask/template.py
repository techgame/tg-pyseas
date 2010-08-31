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

import flask

from pyseas import WebComponent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FlaskTemplate(WebComponent):
    context = {}

    def __init__(self, **context):
        if context:
            self.context = self.updateContext(context, False)

    def renderHtmlOn(self, html):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def renderTemplate(self, html, templateName, **context):
        context = self.updateContext(context, html=html)
        with html.isolated():
            return flask.Markup(flask.render_template(templateName, **context))

    def renderTemplateString(self, html, source, **context):
        context = self.updateContext(context, html=html)
        with html.isolated():
            return flask.Markup(flask.render_template_string(source, **context))

    def updateContext(self, context, selfKey='obj', **kw):
        ctx = self.context.copy()
        if selfKey:
            ctx[selfKey] = self
        ctx.update(context)
        ctx.update(kw)
        return ctx

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FlaskTemplateSource(FlaskTemplate):
    source = None
    def __init__(self, source=None, **context):
        if source is not None:
            self.source = source
        if context:
            self.context = self.updateContext(context, False)

    def renderHtmlOn(self, html):
        return self.renderTemplateString(html, self.source)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FlaskNamedTemplate(FlaskTemplate):
    templateName = None
    def __init__(self, templateName=None, **context):
        if templateName is not None:
            self.templateName = templateName
        if context:
            self.context = self.updateContext(context, False)

    def renderHtmlOn(self, html):
        return self.renderTemplate(html, self.templateName)


