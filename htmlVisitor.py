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

import codecs
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tagContexts = {}

def updateTagContexts(tagList, tagCtx=None, tagContexts=tagContexts):
    if tagCtx is not None:
        for tag in tagList:
            tc = tagContexts.setdefault(tag, {})
            tc.update(tagCtx)
    else:
        if hasattr(tagList, 'items'):
            tagList = tagList.items()

        for tag, tagCtx in tagList:
            tc = tagContexts.setdefault(tag, {})
            tc.update(tagCtx)


forceQuoteChars = u">\"'=&?/; \t\r\n\u000C"
forceQuoteMapping = dict.fromkeys(map(ord, forceQuoteChars), '-')

def mustQuoteAttrValue(value):
    return bool(codecs.charmap_encode(value, 'ignore', forceQuoteMapping)[0])

class entity_charmap_codec(dict):
    def __missing__(self, char): 
        return self.get(unichr(char), char)
    def copy(self):
        return self.__class__(dict.copy(self))
    def encode(self, input, final=False):
        return codecs.charmap_encode(input, 'strict', self)[0]
    def decode(self, input, final=False):
        return codecs.charmap_decode(input, 'strict', self)[0]

_cdataCodec = entity_charmap_codec({"&":"&amp;", "<":"&lt;", ">":"&gt;"})
_attrCodec = entity_charmap_codec({"'":"&apos;", '"':"&quot;"})
_attrCodec.update(_cdataCodec)

def openHtmlIO(host, encoding='utf-8', errors='xmlcharrefreplace'):
    if encoding is None: encoding = 'utf-8'
    if errors is None: errors = 'xmlcharrefreplace'

    fh = codecs.EncodedFile(StringIO(), encoding, encoding, errors)
    def getResult():
        return fh.getvalue()
    def encode(s, encoding=encoding, errors=errors):
        return s.encode(encoding, errors)

    host.write = fh.write
    host.getResult = getResult
    host.encode = encode
    return fh


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlVisitor(object):
    def __init__(self, encoding=None, errors=None):
        self.openHtmlIO(encoding, errors)

    def visit(self, target):
        target.acceptHtmlVisitor(self)

    def append(self, item):
        if hasattr(item, 'acceptHtmlVisitor'):
            self.visit(item)
        elif hasattr(item, '__html__'):
            self.rawMarkup(item.__html__())
        elif isinstance(item, basestring):
            self.cdata(item)
        else:
            raise ValueError('Unable to adapt item to an appropraite type')

    def extend(self, iterable):
        append = self.append
        for each in iterable:
            append(each)

    #~ Attribute Formatting Support ~~~~~~~~~~~~~~~~~~~~~

    mustQuoteAttrValue = staticmethod(mustQuoteAttrValue)

    _attrCodec = _attrCodec
    def fmtAttrEntry(self, key, value, tagCtx={}):
        if not isinstance(value, basestring):
            value = unicode(value)

        encode = self.encode
        key = encode(key.rstrip('_'))
        if key in tagCtx.get('boolAttrs', ["irrelevant"]):
            return key

        value = encode(value)
        if not self.mustQuoteAttrValue(value):
            return key+u'='+value

        value = self._attrCodec.encode(value)
        return key+u'="'+value+u'"'

    def fmtAttrs(self, attrs, tagCtx={}):
        if not attrs:
            return u''

        if hasattr(attrs, "items"):
            attrs = sorted(attrs.items())
        else: attrs.sort()

        fmtAttrEntry = self.fmtAttrEntry
        if attrs:
            r = [u'']
            r.extend(fmtAttrEntry(k,v,tagCtx) for k,v in attrs)
            return u' '.join(r)
        else: return u''


    #~ Tag Open, Close and Context Support ~~~~~~~~~~~~~~

    tagContexts = tagContexts
    def tagOpen(self, tag, attrs=None, selfClose=False):
        tagCtx = self.tagContexts.get(tag, {})
        selfClose = tagCtx.get('selfClose', selfClose)
        if not attrs:
            if selfClose:
                self.write(u'<'+tag+u'/>')
                return False
            else:
                self.write(u'<'+tag+u'>')
                return True

        attrs = self.fmtAttrs(attrs, tagCtx)
        r = [u'<', tag, attrs, '>']
        if selfClose:
            r[-1] = ' />'

        self.write(u''.join(r))
        return not selfClose

    def tagClose(self, tag):
        self.write(u'</'+tag+u'>')

    def withTag(self, tag, attrs=None):
        isOpen = self.tagOpen(tag, attrs, False)
        yield self
        if isOpen:
            self.tagClose(tag)

    def tagElement(self, tag, attrs=None, children=None):
        if children:
            self.tagOpen(tag, attrs, False)
            self.extend(children)
            self.tagClose(tag)
        else:
            if self.tagOpen(tag, attrs, True):
                self.tagClose(tag)


    #~ CDATA Support ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _cdataCodec = _cdataCodec
    def cdata(self, data, escape=True):
        if escape:
            data = self._cdataCodec.encode(data)

        self.write(data)
    text = cdata

    def cdataSection(self, data):
        self.write(u'<![CDATA[')
        self.write(data)
        self.write(u']]>')

    def cdataEntity(self, entityName):
        if not entityName.isalpha():
            raise ValueError("Not a valid entitiy identifier")
        self.write("&"+entityName+';')


    #~ Comment support ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def comment(self, item):
        if hasattr(item, '__html__'):
            item = item.__html__()

        if '--' in item:
            raise ValueError("Comment contains '--'")
        self.write('<!-- '+ comment + ' -->')

    def openComment(self):
        self.write('<!-- ')
        return True
    def closeComment(self):
        self.write(' -->')


    #~ Doctype Support ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _fmtDoctypes = {
        (True, True): u'<!doctype {0} PUBLIC "{1}" SYSTEM "{2}">\n',
        (True, False): u'<!doctype {0} PUBLIC "{1}">\n',
        (False, True): u'<!doctype {0} SYSTEM "{2}">\n',
        (False, False): u'<!doctype {0}>\n',
    }
    def fmtDoctype(self, name='html', publicId=None, systemId=None):
        fmt = self._fmtDoctypes[bool(publicId), bool(systemId)]

        encode = self._attrCodec.encode
        publicId = publicId and encode(publicId)
        systemId = systemId and encode(systemId)

        return fmt.format(name, publicId, systemId)

    def doctype(self, name='html', publicId=None, systemId=None):
        r = self.fmtDoctype(name, publicId, systemId)
        self.write(r)


    #~ Raw Markup Support ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def rawMarkup(self, item):
        if hasattr(item, '__html__'):
            item = item.__html__()
        self.write(item)
    raw = rawMarkup


    #~ Processing Instructions Support ~~~~~~~~~~~~~~~~~~

    def processingInstruction(self, target, instruction):
        if '?>' in target:
            raise ValueError("Processing instruction target contains '?>'")
        if '?>' in instruction:
            raise ValueError("Processing instruction contains '?>'")
        self.write(u'<?'+target+u' '+item+u' ?>')
    PI = processing = processingInstruction


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ HTML IO Methods, provided by openHtmlIO
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    openHtmlIO = openHtmlIO

    def write(self, s):
        raise NotImplementedError('HtmlIO Responsibility')
    def getResult(self):
        raise NotImplementedError('HtmlIO Responsibility')
    def encode(self, s, *args, **kw):
        raise NotImplementedError('HtmlIO Responsibility')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Constants
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

dataRequiredTags = {
    True: 'title textarea style script xmp iframe noembed noframes noscript div span',
    False: 'base command event-source link meta hr br img embed param area col input source',
}

tagBoolAttrs = '''
    style   : irrelevant scoped
    img     : irrelevant ismap
    audio   : irrelevant autoplaycontrols
    video   : irrelevant autoplaycontrols
    script  : irrelevant defer async
    details : irrelevant open
    datagrid: irrelevant multiple disabled
    command : irrelevant hidden disabled checked default
    hr      : irrelevant noshade
    menu    : irrelevant autosubmit
    fieldset: irrelevant disabled readonly
    option  : irrelevant disabled readonly selected
    optgroup: irrelevant disabled readonly
    button  : irrelevant disabled autofocus
    input   : irrelevant disabled readonly required autofocus checked ismap
    select  : irrelevant disabled readonly autofocus multiple
    output  : irrelevant disabled readonly
'''.split('\n')

tagBoolAttrs = [e.strip().partition(':') for e in tagBoolAttrs]
tagBoolAttrs = [(k.strip(), {'boolAttrs':v.split()}) for k,e,v in tagBoolAttrs if e]
del e,k,v

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def _updateTagAttrs():
    updateTagContexts(tagBoolAttrs)
    for e,v in dataRequiredTags.items():
        updateTagContexts(v.split(), {'selfClose': not e})
_updateTagAttrs()
del _updateTagAttrs

