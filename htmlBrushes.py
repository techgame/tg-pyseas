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
import functools

from lxml import etree
from lxml.html import fragments_fromstring

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ HTML Brush Attrs
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlAttrs(object):
    def __init__(self, *args, **kw):
        if args or kw:
            self.__dict__.update(*args, **kw)

    @property
    def ns(self): return self.__dict__

    def asXMLAttrib(self):
        attrib = {}
        for k, v in self.items():
            if not isinstance(v, basestring):
                v = str(v)
            attrib[k.rstrip('_')] = v
        return attrib

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
    def __init__(self, bctx, tag, *args, **kw):
        self._bctx = bctx
        self.tag = tag
        self.initBase()
        self.initBrush(args, kw)
        if bctx is not None:
            bctx.onBrushCreated(self)

    def new(self, *args, **kw):
        return self.__class__(None, self.tag, *args, **kw)
    def copy(self):
        raise NotImplementedError("Copy not implemented for %s"%(self.__class__.__name__,))

    def isBrush(self):
        return True
    def asBrush(self, bctx=None):
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

    def __html__(self):
        return self.asXMLString(pretty_print=True)

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
    attrs = HtmlAttrs()

    def initBase(self):
        super(HtmlListBaseBrush,self).initBase()
        self._elements = []

    def copy(self):
        """Deep copy of brush"""
        return self.new(*(e.copy() for e in self._elements), **self.attrs)

    def __enter__(self):
        self._bctx.pushBrush(self)
        return self
    def __exit__(self, excType, exc, tb):
        assert self._bctx.popBrush() is self


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
        elem.attrib.update(self.attrs.asXMLAttrib())
        for e in self.elements:
            e = e.asElementTree(elem)
            if e is not None:
                elem.append(e)

    def copyElementsTo(self, target):
        if etree.iselement(target):
            for e in self.elements:
                e.asElementTree(target)
        else:
            target.extend(e.copy() for e in self.elements)
        return target
    def moveElementsTo(self, target):
        elements = self.elements
        self._elements = []
        if etree.iselement(target):
            for e in elements:
                e.asElementTree(target)
        else:
            target.extend(elements)
        return target

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
        if item is None: return
        adaptor = self.adaptorForItem(item)
        item = adaptor(item, self._bctx)
        if item is None: return
        if isinstance(item, dict):
            return self.addAttrs(item)
        elif isinstance(item, list):
            return self.extend(item)
        return self.addBrush(item)

    def add(self, item):
        if item is None: return
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
        list: (lambda item,bctx: item),
        dict: (lambda item,bctx: item),
        str: (lambda item,bctx: bctx.text(item)),
        unicode: (lambda item,bctx: bctx.text(item)),
        }
    def adaptorForItem(self, item):
        try: return item.asBrush
        except AttributeError: pass

        aMap = self.adaptorMap
        for kind in type(item).mro():
            entry = aMap.get(kind)
            if entry is not None:
                return entry
        print (item, type(item))
        raise ValueError("No adpator for result: %r" %(item,) )


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Tag Brushes with sub-elements and callbacks
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tagCallbackAttrMap = {
    'a': 'href',
    'form': 'action',
}

class HtmlTagBrush(HtmlListBaseBrush):
    attrs = HtmlListBaseBrush.attrs.copy()

    def initBrush(self, elems, kwattrs):
        attrs = self.attrs.copy()
        if kwattrs:
            attrs.update(kwattrs)
        self.attrs = attrs
        if elems:
            self.extend(elems)

    #~ callback binding ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def bind(self, callback, *args, **kw):
        return self.ctxBindEx(None, callback, args, kw)
    def ctxBind(self, context, callback, *args, **kw):
        return self.ctxBindEx(context, callback, args, kw)
    def ctxBindEx(self, context, callback, args, kw):
        if args or kw:
            callback = functools.partial(callback, *args, **kw)
        return self.callback(callback, context)
    def callback(self, callback, context=None):
        url = self._bctx.callback(callback, context)
        self.setCallbackUrl(url)
        return self

    _tagCallbackAttrMap = tagCallbackAttrMap
    def setCallbackUrl(self, url):
        key = self._tagCallbackAttrMap[self.tag]
        self.attrs[key] = url

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Subclasses with useful defaults
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlForm(HtmlTagBrush):
    attrs = HtmlTagBrush.attrs.branch(
        method='POST', enctype='multipart/form-data')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Text Base Brushes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlText(HtmlBaseBrush):
    def initBrush(self, args, kw):
        self.text = ''.join(args)

    def copy(self):
        return self.new(self.text)

    def asElementTree(self, parent):
        if len(parent):
            e = parent[-1]
            e.tail = (e.tail or '') + self.text
        else:
            parent.text = (parent.text or '') + self.text

class HtmlEntity(HtmlBaseBrush):
    def initBrush(self, args, kw):
        if args:
            self.entity = etree.Entity(args[0])
    def asElementTree(self, parent):
        parent.append(self.entity)

class HtmlSpace(HtmlEntity):
    entity = etree.Entity('nbsp')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Raw Brushes for HTML Source or Lxml elements
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlRaw(HtmlListBaseBrush):
    parseFragments = staticmethod(fragments_fromstring)

    def initBrush(self, args, kw):
        self.fragments = self.parseFragments(''.join(args))

    def copy(self):
        raise NotImplementedError("Copy not implemented for HtmlRaw brushes")

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

html5HeadTags = """
    head title meta link noscript script style base""".split()

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
    entity = HtmlEntity,

    raw = HtmlRaw,
    xml = HtmlRaw,

    lxml = HtmlLxml,
    etree = HtmlLxml,
    )
