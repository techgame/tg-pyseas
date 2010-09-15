# -*- coding: utf-8 -*-
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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ConfirmWidget(WebComponent):
    cssClass = 'confirm-question'
    message = "Confirm?"
    yes = "Yes"
    no = "No"

    def __init__(self, message=None, yes=None, no=None):
        if message is not None:
            self.message = message
        if yes is not None:
            self.yes = yes
        if no is not None:
            self.no = no

    def renderHtmlOn(self, html):
        with html.span(class_=self.cssClass):
            html.strong(self.message)
            html.nbsp()
            html.a(self.yes).bind(self.answer, True)
            html.nbsp()
            html.a(self.no).bind(self.answer, False)

