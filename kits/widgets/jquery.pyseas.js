/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2010  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

(function( $, undefined) {
    var defaults = {
        rootSelector: '.wc-ajax',
        ctxUrl: ctxUrl,
    }
    var module = {
        init: function() {
        },
        each: function(args, callback, options) {
            var opts = $.extend({}, $.fn.pyseas.defaults, options)
            return this.closest(opts.rootSelector).each(
                function(i,elem){
                    callback.call(this, i, elem,
                        module.ctxUrlJoin.call(this, elem.id, args, opts.ctxUrl))
                })
        },

        call: function(args, callback, options) {
            if (!$.isFunction(callback) && !options) {
                options = callback;
                callback = undefined;
            }
            var opts = $.extend({}, $.fn.pyseas.defaults, options)
            return module.each.call(this, args, performCall, opts)

            function performCall(i,elem,url) {
                $.ajax($.extend({}, opts, {
                    url:url, 
                    success:function(data) {
                        if (callback) callback.call(this, $(data))
                    }
                }))
            }
        },

        load: function(args, callback, options) {
            if (!$.isFunction(callback) && !options) {
                options = callback;
                callback = undefined;
            }
            var opts = $.extend({}, $.fn.pyseas.defaults, options)
            return module.each.call(this, args, performLoad, opts)

            function performLoad(i, elem, url) {
                $.ajax($.extend({}, opts, {
                    url:url, 
                    success: function(data) {
                        data = $(data)
                        $(elem).replaceWith(data)
                        if (callback) callback.call(this, data)
                    }
                }))
            }
        },

        ctxUrlJoin: function(key, args, url) {
            if (!url) url = $.fn.pyseas.defaults.ctxUrl
            var r = [url, "!x="+encodeURIComponent(key)]
            if (args) r.push($.param(args))
            return r.join("&")
        },
    }

    $.fn.pyseas = function( method ) {
        if (module[method]) {
            return module[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if (!method || typeof method === 'object') {
            return module.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.pyseas' );
        }
    };
    $.fn.pyseas.defaults = defaults
        
})(jQuery);
