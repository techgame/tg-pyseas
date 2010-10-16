/*
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2010  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
*/

var ctxUrl = ctxUrl || {};

(function( $, undefined) {
    function _ctxJoin(key, args, urlMap) {{
        if (!urlMap) urlMap = ctxUrl;
        var r = [urlMap[key.split('-')[0]], 
                "!x="+encodeURIComponent(key), 
                $.param(args)]
        return r.join("&")
    }}

    $.fn.pyseasCall = function(args, data, callback, options) {
        if (!this.length) return this;
        if (args === undefined) args = {}
        if ($.isFunction(data)) {
            options = callback
            callback = data
            data = undefined
        }

        var opts = $.extend({}, $.fn.pyseasCall.defaults, options)
        return this.closest(opts.host).each(function(idx, e) {
            var url = _ctxJoin(e.id, args, opts.ctxUrl);
            return $(e).load(url, data, callback); 
        })
    }
    $.fn.pyseasCall.defaults = {
        host: '.oid',
        ctxUrl: ctxUrl,
    };
})(jQuery);
