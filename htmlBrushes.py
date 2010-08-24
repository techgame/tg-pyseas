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
from itertools import izip_longest

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

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
    def __init__(self, bctxRef, tag, *args, **kw):
        self._bctx = bctxRef
        self.tag = tag
        self.initBase()
        self.initBrush(args, kw)
        if bctxRef is not None:
            bctxRef().onBrushCreated(self)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.tag)

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

    def parent(self):
        return None

    def onAddedToBrush(self, parent, explicit=False):
        if parent is not self.parent():
            self.parent = weakref.ref(parent)
            return True

    def orphan(self):
        self.parent = None
        del self.parent
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __html__(self):
        from .htmlVisitor import HtmlVisitor
        hv = HtmlVisitor()
        hv.append(self)
        return hv.getResult()

    def acceptHtmlVisitor(self, htmlVis):
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

    attrib = property(lambda self: self.attrs)

    def __enter__(self):
        self._bctx().pushBrush(self)
        return self
    def __exit__(self, excType, exc, tb):
        if self._bctx().popBrush() is not self:
            raise RuntimeError("Brush stack mistmatch")


    def __len__(self):
        return len(self.elements)
    def __iter__(self):
        return iter(self.elements)

    def getElements(self):
        el = self._elements
        el[:] = [e for e in el if e.parent() is self]
        return el
    elements = property(getElements)

    def acceptHtmlVisitor(self, htmlVis):
        htmlVis.tagElement(self.tag, self.attrs, self.elements)

    def copyElementsTo(self, target):
        target.extend(e.copy() for e in self.elements)
        return target
    def moveElementsTo(self, target):
        elements = self.elements
        self._elements = []
        target.extend(elements)
        return target

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addImplicitBrush(self, brush):
        if brush.onAddedToBrush(self, False):
            self._elements.append(brush)
        return brush
    def addBrush(self, brush):
        if brush.onAddedToBrush(self, True):
            self._elements.append(brush)
        return brush
    def addAttrs(self, attrs):
        self.attrs.update(attrs)
        return attrs
    def addItem(self, item):
        if item is None: return
        adaptor = self.adaptorForItem(item)

        with self:
            item = adaptor(item, self._bctx())

        if item is not None: 
            if isinstance(item, dict):
                return self.addAttrs(item)
            elif isinstance(item, list):
                return self.extend(item)
            else:
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

        'html': (lambda item,bctx: bctx.raw(item.__html__())),
        'component': (lambda item,bctx: bctx.render(item))
        }
    def adaptorForItem(self, item):
        aMap = self.adaptorMap
        try: return item.asBrush
        except AttributeError: pass

        try: 
            if item.isWebComponent():
                return aMap['component']
        except AttributeError: 
            pass

        try: 
            if item.__html__:
                return aMap['html']
        except AttributeError: 
            pass

        for kind in type(item).mro():
            entry = aMap.get(kind)
            if entry is not None:
                return entry

        raise ValueError("No adpator for result: %r" %(item,) )


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Tag Brushes with sub-elements and callbacks
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlTagBrush(HtmlListBaseBrush):
    attrs = HtmlListBaseBrush.attrs.copy()
    _callbackUrlKey = 'href'

    def initBrush(self, elems, kwattrs):
        attrs = self.attrs.copy()
        if kwattrs:
            attrs.update(kwattrs)
        self.attrs = attrs
        if elems:
            self.extend(elems)

    #~ callback binding ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def bind(self, callback, *args, **kw):
        if args or kw:
            callback = functools.partial(callback, *args, **kw)
        return self.callback(callback)
    def callback(self, callback, **tagAttrs):
        url, attrs = self._bctx().callbackUrlAttrs(callback, **tagAttrs)
        self.setCallbackUrl(url, attrs)
        return self

    def setCallbackUrl(self, url, cbAttrs):
        attrs = self.attrs
        attrs.update(cbAttrs)
        attrs[self._callbackUrlKey] = url

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Subclasses with useful defaults
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlForm(HtmlTagBrush):
    attrs = HtmlTagBrush.attrs.branch(
        method='POST', enctype='multipart/form-data')
    _callbackUrlKey = 'action'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Text Base Brushes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlText(HtmlBaseBrush):
    def initBrush(self, args, kw):
        self.text = ''.join(args)

    def copy(self):
        return self.new(self.text)

    def acceptHtmlVisitor(self, htmlVis):
        htmlVis.cdata(self.text)

class HtmlEntity(HtmlBaseBrush):
    entity = 'nbsp'
    def initBrush(self, args, kw):
        if args:
            self.entity, = args
    def acceptHtmlVisitor(self, htmlVis):
        htmlVis.cdataEntity(self.entity)

class HtmlSpace(HtmlEntity):
    entity = 'nbsp'

class HtmlDoctype(HtmlBaseBrush):
    def initBrush(self, args, kw):
        self.setDoctype(*args, **kw)

    def setDoctype(self, name='html', publicId=None, systemId=None):
        self.name = name
        self.publicId = publicId
        self.systemId = systemId

    def acceptHtmlVisitor(self, htmlVis):
        htmlVis.doctype(self.name, self.publicId, self.systemId)


class HtmlDocument(HtmlListBaseBrush):
    def initBrush(self, elems, kw):
        if elems:
            self.extend(elems)

    def acceptHtmlVisitor(self, htmlVis):
        htmlVis.extend(self.elements)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Raw Brushes for HTML Source
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HtmlRaw(HtmlListBaseBrush):
    def initBrush(self, args, kw):
        self.fragments = list(args)

    def copy(self):
        newSelf = self.new()
        self.copyElementsTo(newSelf)
        return newSelf

    def acceptHtmlVisitor(self, htmlVis):
        for frag,elem in izip_longest(self.fragments, self.elements):
            if frag is not None:
                htmlVis.rawMarkup(frag)
            if elem is not None:
                htmlVis.append(elem)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Utility Brushes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NothingBrush(object):
    def __init__(self, bctxRef=None, tag=None):
        pass
    def __enter__(self):
        pass
    def __exit__(self, excType, exc, tb):
        pass

class IsolatedBrush(HtmlListBaseBrush):
    def __html__(self):
        return ''
    def acceptHtmlVisitor(self, htmlVis):
        pass

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

# add default tag -> HtmlTagBrush factories for valid tags
htmlTagBrushMap = dict((tag, HtmlTagBrush) for tag in html5Tags)
htmlTagBrushMap.update(form = HtmlForm, )

html5HeadTags = """
    head title meta link noscript script style base""".split()

htmlHeadTagBrushMap = dict((tag, htmlTagBrushMap[tag]) for tag in html5HeadTags)

html5ContentAttributeEvents = """
    onabort onerror onmousewheel onblur onfocus onpause oncanplay onformchange
    onplay oncanplaythrough onforminput onplaying onchange oninput onprogress
    onclick oninvalid onratechange oncontextmenu onkeydown onreadystatechange
    ondblclick onkeypress onscroll ondrag onkeyup onseeked ondragend onload
    onseeking ondragenter onloadeddata onselect ondragleave onloadedmetadata onshow
    ondragover onloadstart onstalled ondragstart onmousedown onsubmit ondrop
    onmousemove onsuspend ondurationchange onmouseout ontimeupdate onemptied
    onmouseover onvolumechange onended onmouseup onwaiting """.split()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

htmlUtilityTagBrushMap = dict(
    nothing = NothingBrush,
    isolated = IsolatedBrush,

    document = HtmlDocument,
    doctype = HtmlDoctype,

    text = HtmlText,
    space = HtmlSpace,
    entity = HtmlEntity,

    raw = HtmlRaw,)


for brushMap in [htmlHeadTagBrushMap, htmlTagBrushMap]:
    brushMap.update(htmlUtilityTagBrushMap)

