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

import functools
import flask

from TG.pyseas.component import WebComponent
from TG.pyseas import sessionComponent as base

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sessionFactory = functools.partial(base.bindSessionFactory, flask.session)

def sessionProxy(factory, *args, **kw):
    lookupFn = sessionFactory(factory, *args, **kw)
    return flask.globals.LocalProxy(lookupFn)

class FlaskComponent(WebComponent):
    sessionProxy = classmethod(sessionProxy)
    sessionFactory = classmethod(sessionFactory)

class FlaskSessionComponent(base.SessionComponent):
    session = flask.session

