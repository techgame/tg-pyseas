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

from urllib import quote, urlencode

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UrlToolsMixin(object):
    urlencode = staticmethod(urlencode)

    def newUrl(self, _url_, *args, **kw):
        if args: kw = dict(*args, **kw)
        query = '&'.join(quote(str(k))+'='+quote(str(v)) for k,v in kw.iteritems())
        return self.newUrlQuery(_url_, query)
    url = newUrl

    def newUrlEncode(self, _url_, *args, **kw):
        if args: kw = dict(*args, **kw)
        return self.newUrlQuery(_url_, self.urlencode(kw))

    def newUrlQuery(self, url, query):
        return url.split('?', 1)[0]+'?'+query

