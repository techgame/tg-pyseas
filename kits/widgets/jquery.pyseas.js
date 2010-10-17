/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2010  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

(function( $, undefined) {
    var defaults = {
        host: '.wc-ajax',
        ctxUrl: ctxUrl,
    }
    function _ctxJoin(url, key, args) {
        var r = [url, "!x="+encodeURIComponent(key)]
        if (args) r.push($.param(args))
        return r.join("&")
    }
    $.fn.pyseasCall = function(args, callback, options) {
        if (!this.length) return this;
        if (!$.isFunction(callback) && !options) {
            options = callback;
            callback = undefined;
        }

        var opts = $.extend({}, $.fn.pyseasCall.defaults, options)
        return this.closest(opts.host).each(_loadHostReplacement)

        function _loadHostReplacement(i, elem) {
            var url = _ctxJoin(opts.ctxUrl, elem.id, args);
            function success(data) { 
                data = $(data);
                $(elem).replaceWith(data);
                if (callback) callback.call(this, data)
            }
            $.ajax($.extend({url:url, success:success}, opts))
        }
    }
    $.fn.pyseasCall.defaults = defaults
})(jQuery);
