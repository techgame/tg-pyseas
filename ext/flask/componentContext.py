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

from pyseas.session import ComponentContext

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FlaskComponentContext(ComponentContext):
    g_attrname = 'componentContext'
    redirect = staticmethod(flask.redirect)

    @classmethod
    def sessionContext(klass, sessionKey):
        if not hasattr(sessionKey, 'lookup'):
            mgr = klass.sessionManager(sessionKey)
        else: mgr = sessionKey

        def contextSession(mgr=mgr):
            self = getattr(flask.g, klass.g_attrname, None)
            if self is None:
                self = mgr.lookup(flask.session)
                setattr(flask.g, klass.g_attrname, self)
            return self

        return flask.globals.LocalProxy(contextSession)

    def context(self, request=flask.request):
        return self.RequestContext(self, request.path, request.args)

