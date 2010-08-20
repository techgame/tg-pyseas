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

import weakref

from lxml import etree
from lxml.html import fragments_fromstring

from .callbackMap import CallbackRegistrationMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ HTML Brush Attrs
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlAttrs(object):
    def __init__(self, *args, **kw):
        if args or kw:
            self.__dict__.update(*args, **kw)

    @property
    def ns(self): return self.__dict__

    def copy(self):
        return self.__class__(self.ns)
    def branch(self, *args, **kw):
        r = self.copy() 
        r.update(*args, **kw)
        return r

    def update(self, *args, **kw):
        self.__dict__.update(*args, **kw)

    def __len__(self):
        return len(self.ns)
    def __iter__(self):
        return self.ns.iteritems()
    def __contains__(self, key):
        return key in self.ns
    def get(self, key, default=None):
        return self.ns.get(key, default)
    def __getitem__(self, key):
        return self.ns[key]
    def __setitem__(self, key, value):
        self.ns[key] = value
    def __delitem__(self, key):
        del self.ns[key]

    def keys(self): return self.ns.keys()
    def values(self): return self.ns.values()
    def items(self): return self.ns.items()
    def iterkeys(self): return self.ns.iterkeys()
    def itervalues(self): return self.ns.itervalues()
    def iteritems(self): return self.ns.iteritems()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ HTML Base Brush
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlBaseBrush(object):
    def __init__(self, html, tag, *args, **kw):
        self.tag = tag
        self._html_ = html
        self.initBase()
        self.initBrush(args, kw)
        html.onBrushCreated(self)

    def isBrush(self):
        return True
    def asBrush(self, html=None):
        return self

    def initBase(self):
        pass
    def initBrush(self, args, kw):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    parent = None
    def onAddedToBrush(self, parent, explicit=False):
        self.parent = weakref.ref(parent)

    def orphan(self):
        self.parent = lambda: None
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def asXMLString(self, **kw):
        root = etree.Element('ROOT')
        self.asElementTree(root)
        return ''.join(etree.tostring(e, **kw) for e in root)

    def asElementTree(self, parent):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ HTML Tag Brush
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlListBaseBrush(HtmlBaseBrush):
    def initBase(self):
        super(HtmlListBaseBrush,self).initBase()
        self._elements = []

    def __enter__(self):
        self._html_.pushBrush(self)
        return self
    def __exit__(self, excType, exc, tb):
        assert self._html_.popBrush() is self


    def __len__(self):
        return len(self.elements)
    def __iter__(self):
        return iter(self.elements)

    def getElements(self):
        el = self._elements
        el[:] = [e for e in el if e.parent() is self]
        return el
    elements = property(getElements)

    def asElementTree(self, parent):
        elem = etree.SubElement(parent, self.tag)
        elem.attrib.update(self.attrs)
        for e in self.elements:
            e = e.asElementTree(elem)
            if e is not None:
                elem.append(e)

    def moveElements(self, parent):
        elements = self.elements
        self._elements = []
        if etree.iselement(parent):
            for e in elements:
                e.asElementTree(parent)
        else:
            parent.extend(elements)
        return parent

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addImplicitBrush(self, brush):
        brush.onAddedToBrush(self, False)
        self._elements.append(brush)
    def addBrush(self, brush):
        brush.onAddedToBrush(self, True)
        self._elements.append(brush)
        return brush
    def addAttrs(self, attrs):
        self.attrs.update(attrs)
        return attrs
    def addItem(self, item):
        adaptor = self.adaptorForItem(item)
        item = adaptor(item, self._html_)
        if isinstance(item, dict):
            return self.addAttrs(item)
        elif isinstance(item, list):
            return self.extend(item)
        return self.addBrush(item)

    def add(self, item):
        try: brush = item.asBrush()
        except AttributeError:
            return self.addItem(item)
        return self.addBrush(brush)
    def append(self, item):
        self.add(item)
        return self
    def extend(self, items):
        for e in items:
            self.add(e)
        return self

    adaptorMap = {
        list: (lambda item,html: item),
        dict: (lambda item,html: item),
        str: (lambda item, html: html.text(item)),
        unicode: (lambda item, html: html.text(item)),
        }
    def adaptorForItem(self, item):
        try: return item.asBrush
        except AttributeError: pass

        aMap = self.adaptorMap
        for kind in type(item).mro():
            entry = aMap.get(kind)
            if entry is not None:
                return entry

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tagCallbackAttrMap = {
    'a': 'href',
    'form': 'action',
}

class HtmlTagBrush(HtmlListBaseBrush, CallbackRegistrationMixin):
    attrs = HtmlAttrs()

    def initBrush(self, elems, kwattrs):
        attrs = self.attrs.copy()
        if kwattrs:
            attrs.update(kwattrs)
        self.attrs = attrs
        if elems:
            self.extend(elems)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def callback(self, callback, context=None):
        url = self._html_.callback(callback, context)
        self.setCallbackUrl(url)
        return self

    _tagCallbackAttrMap = tagCallbackAttrMap
    def setCallbackUrl(self, url):
        key = self._tagCallbackAttrMap[self.tag]
        self.attrs[key] = url

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class HtmlForm(HtmlTagBrush):
    attrs = HtmlTagBrush.attrs.branch(
                method='POST', 
                enctype="multipart/form-data")


class HtmlText(HtmlBaseBrush):
    def initBrush(self, args, kw):
        text = ''.join(args)
        self.text = text.format(**kw)

    def asElementTree(self, parent):
        if len(parent):
            e = parent[-1]
            e.tail = (e.tail or '') + self.text
        else:
            parent.text = (parent.text or '') + self.text

class HtmlSpace(HtmlText):
    def initBrush(self, args, kw):
        if args or kw:
            raise ValueError("HtmlSpace takes no parameters")
        self.text = "&nbsp;"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlRaw(HtmlListBaseBrush):
    parseFragments = staticmethod(fragments_fromstring)

    def initBrush(self, args, kw):
        fragments = ''.join(args)
        fragments = fragments.format(**kw)
        self.fragments = self.parseFragments(fragments)

    def asElementTree(self, parent):
        parent.extend(self.fragments)
        for e in self.elements:
            e.asElementTree(parent)

class HtmlLxml(HtmlRaw):
    def initBrush(self, args, kw):
        fragments = []
        for e in args:
            if not etree.iselement(e):
                e = etree.XML(e)
            fragments.append(e)
        self.fragments = fragments

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ HTML Brush Tags 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

html5Tags = """
    a abbr address area article aside audio b base bdo blockquote body br
    button canvas caption cite code col colgroup command datalist dd del
    details dfn div dl dt em embed eventsource fieldset figcaption figure
    footer form h1 h2 h3 h4 h5 h6 head header hgroup hr html i iframe img input
    ins kbd keygen label legend li link mark map menu meta meter nav noscript
    object ol optgroup option output p param pre progress q ruby rp rt samp
    script section select small source span strong style sub summary sup table
    tbody td textarea tfoot th thead time title tr ul var video wbr""".split()

html5ContentAttributeEvents = """
    onabort onerror onmousewheel onblur onfocus onpause oncanplay onformchange
    onplay oncanplaythrough onforminput onplaying onchange oninput onprogress
    onclick oninvalid onratechange oncontextmenu onkeydown onreadystatechange
    ondblclick onkeypress onscroll ondrag onkeyup onseeked ondragend onload
    onseeking ondragenter onloadeddata onselect ondragleave onloadedmetadata onshow
    ondragover onloadstart onstalled ondragstart onmousedown onsubmit ondrop
    onmousemove onsuspend ondurationchange onmouseout ontimeupdate onemptied
    onmouseover onvolumechange onended onmouseup onwaiting """.split()

# add default tag -> HtmlTagBrush factories for valid tags
htmlTagBrushMap = dict((tag, HtmlTagBrush) for tag in html5Tags)
htmlTagBrushMap.update(
    form = HtmlForm,
    text = HtmlText,
    space = HtmlSpace,

    raw = HtmlRaw,
    xml = HtmlRaw,

    lxml = HtmlLxml,
    etree = HtmlLxml,
    )
