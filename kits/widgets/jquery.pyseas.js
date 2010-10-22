/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2010  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

(function( $, undefined) {
    var defaults = {
        args: null,
        root: '.wc-ajax',
        ctxUrl: ctxUrl,

        settings: {
            /* jQuery.ajax options */
            async: true,
            global: false,
            type: 'POST',
            contentType: 'application/json'
        }
    }
    var module = {
        init: function() {
            this.trigger('pyseasLoad', {init:true})
        },

        invoke: function(options) {
            var opt = $.extend({}, $.fn.pyseas.defaults, options)
            opt.settings = $.extend({}, opt.settings,
                {data: JSON.stringify(opt.data || {})})
            return this.closest(opt.root).each(function(i, elem) {
                $.ajax($.extend({}, opt.settings, {
                    url: module.urlJoin(elem, opt),
                    success:function(response) {
                        if (opt.callback) opt.callback.call(this, $(response), $(elem))
                    }}))
                })
        },

        load: function(options) {
            var opt = $.extend({}, $.fn.pyseas.defaults, options)
            opt.settings = $.extend({}, opt.settings,
                {data: JSON.stringify(opt.data || {})})
            return this.closest(opt.root).each(function(i, elem) {
                $.ajax($.extend({}, opt.settings, {
                    url: module.urlJoin(elem, opt),
                    success: function(response) {
                        elem = $(elem)
                        response = $(response)
                        elem.replaceWith(response)
                        if (opt.callback) opt.callback.call(this, response, elem)
                        response.trigger('pyseasLoad', {})
                    }}))
                })
        },

        urlJoin: function(elem, options) {
            var r = [options.ctxUrl, "!x="+encodeURIComponent(elem.id)]
            if (options.args) r.push($.param(options.args))
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
