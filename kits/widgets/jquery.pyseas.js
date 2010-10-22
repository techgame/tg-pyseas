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

        /* jQuery.ajax options */
        async: true,
        global: false,
        type: 'POST'
    }
    var module = {
        init: function() {
            this.trigger('pyseasLoad', {init:true})
        },

        _unpackArgs: function(args, callback, options) {
            if ($.isFunction(args) && !callback && !options) {
                callback = args;
                args = undefined;
            } else if (!$.isFunction(callback) && !options) {
                options = callback;
                callback = undefined;
            }
            options = $.extend({}, $.fn.pyseas.defaults, options)
            return [args, callback, options]
        },

        each: function(args, callback, options) {
            var r = module._unpackArgs.apply(this, arguments)
            args = r[0]; callback = r[1]; options = r[2];
            return this.closest(options.rootSelector).each(
                function(i,elem){
                    var url = module.ctxUrlJoin.call(this, elem.id, args, options.ctxUrl)
                    callback.call(this, i, elem, url)
                })
        },

        invoke: function(args, callback, options) {
            var r = module._unpackArgs.apply(this, arguments)
            args = r[0]; callback = r[1]; options = r[2];
            return module.each.call(this, args, performInvoke, options)

            function performInvoke(i, elem, url) {
                elem = $(elem)
                $.ajax($.extend({}, options, {
                    url:url,
                    success:function(response) {
                        response = $(response)
                        if (callback) callback.call(this, response, elem)
                    }
                }))
            }
        },

        load: function(args, callback, options) {
            var r = module._unpackArgs.apply(this, arguments)
            args = r[0]; callback = r[1]; options = r[2];
            return module.each.call(this, args, performLoad, options)

            function performLoad(i, elem, url) {
                elem = $(elem)
                $.ajax($.extend({}, options, {
                    url:url,
                    success: function(response) {
                        response = $(response)
                        elem.replaceWith(response)
                        if (callback) callback.call(this, response, elem)
                        response.trigger('pyseasLoad', {})
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
