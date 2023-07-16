# -*- coding: latin-1 -*-

# Simple json-format
#
# Possible improvements:
# - produce nicer JSON
# - omit default arguments



from pynotebook.textmodel.textmodel import TextModel
from pynotebook.nbtexels import TextCell, ScriptingCell, mk_textmodel, \
    Graphics, BitmapRGBA, BitmapRGB
from pynotebook.graphics import LineColor, LineWidth, LineDashes, LineJoin, \
    LineCap, FillColor, Line, Polygon, Path, Circle, Ellipse, Arc, \
    Rectangle, Font, GraphicsText, Translate, Rotate, Scale
from pynotebook.textmodel.texeltree import Group, Text, NewLine, Tabulator, G,\
    T, dump, EMPTYSTYLE, NULL_TEXEL, grouped, hash_style
from functools import reduce
from base64 import b64encode
import json


magic = '# pynotebook1\n'

def _flatten(g):
    if not isinstance(g, Group):
        return [g]      
    r = []
    for child in g.childs:
        r.extend(_flatten(child))
    return r


def _join_strings(l, b):
    if len(l) == 0:
        return [b]
    a = l[-1]
    if 1: # jupyter style
        if a.endswith('\n'):
            return l+[b]
    return l[:-1]+[a+b]
    

string_classes = Text, NewLine, Tabulator
def _join_text(l, b):
    # merge texel l[-1] and b if they are both similarly formatted strings. 
    if len(l) == 0:
        return [b]
    a = l[-1]
    if 1:
        # jupyter starts a new element after each \n
        if a.text.endswith('\n'):
            return l+[b]
    if isinstance(b, NewLine): # and b.parstyle:
        return l+[b]
    if a.__class__ in string_classes and b.__class__ in string_classes:
        if a.style is b.style:
            return l[:-1]+[Text(a.text+b.text)]
    return l+[b]

def _break_string(s, w=80):
    r = []
    while len(s) > w:
        r.append(s[:w])
        s = s[w:]
    return r+[s]
                 

class _TexelProcessor:
    def __init__(self, texel):
        self._current_style = {}
        self._defined_styles = dict()
        self._current_parstyle = {}
        self._defined_parstyles = dict()        
        self.result = self.process(texel)
        
    def process(self, texel):
        name = "handle_"+texel.__class__.__name__
        f = getattr(self, name)
        return f(texel)

    ### texeltree
    def handle_Group(self, texel):
        return [self.process(x) for x in _flatten(texel)]

    def set_style(self, style):
        r = []
        if style is not self._current_style:
            h = hash_style(style)
            if h not in self._defined_styles:
                # Achtung: definiert und setzt den Style
                name = 'S%i' % len(self._defined_styles)
                self._defined_styles[h] = name
                cmd = dict(cmd='newstyle', name=name)
                cmd.update(style)
                r.append(cmd)
            else:
                name = self._defined_styles[h]
                cmd = dict(cmd='style', name=name)
                r.append(cmd)
                r.append(dict(style=name))
            self._current_style = style
        return r

    def set_parstyle(self, parstyle):
        r = []
        if parstyle is not self._current_parstyle:
            h = hash_style(parstyle)
            if h not in self._defined_parstyles:
                # Achtung: definiert und setzt den Style
                name = 'PS%i' % len(self._defined_parstyles)
                self._defined_parstyles[h] = name
                cmd = dict(cmd='newparstyle', name=name)
                cmd.update(parstyle)
                r.append(cmd)
            else:
                name = self._defined_parstyles[h]
                cmd = dict(cmd='parstyle', name=name)
                r.append(cmd)
                r.append(dict(parstyle=name))
            self._current_parstyle = parstyle
        return r
    
    def handle_Text(self, texel):
        #return [dict(cls=texel.__class__.__name__, style=texel.style, text=texel.text)]
        return self.set_style(texel.style)+_break_string(texel.text)
    
    def handle_NewLine(self, texel):
        return self.set_style(texel.style)+\
               self.set_parstyle(texel.parstyle)+['\n']

    def handle_Tabulator(self, texel):
        return dict(cls=texel.__class__.__name__, style=texel.style, parstyle=texel.parstyle)
    
    def handle_RichText(self, texel):
        # Richtext can contain any texel, including formatted text
        childs = reduce(_join_text, _flatten(texel), [])
        r = []
        for x in childs:
            r.extend(self.process(x))
        return r

    def handle_UnformattedText(self, texel):
        strings = [t.text for t in _flatten(texel)]
        return reduce(_join_strings, strings, [])

    ### nbtexels
    def handle_TextCell(self, texel):
        return [dict(
            cls=texel.__class__.__name__,
            text=self.handle_RichText(texel.text))]
    
    def handle_ScriptingCell(self, texel):
        return [dict(
            cls=texel.__class__.__name__,
            client=texel.client_name,
            input=self.handle_UnformattedText(texel.input), 
            output=self.handle_RichText(texel.output))]
    
    def handle_BimapRGB(self, texel):
        return [dict(
            cls=texel.__class__.__name__,
            size=texel.size,
            data=_break_string(texel.data.decode('latin-1'), 20))]

    def handle_BitmapRGBA(self, texel):
        return [dict(
            cls=texel.__class__.__name__,
            size=texel.size,
            data=_break_string(texel.data.decode('latin-1'), 20),
            alpha=_break_string(texel.alpha.decode('latin-1'), 20))]

    def handle_Graphics(self, texel):
        l = []
        for item in texel.items:
            l += self.process(item)
        return [dict(
            cls=texel.__class__.__name__,            
            items=l,
            size=texel.size,
            frame=texel.frame)]
    ### graphics
    
    #def _dump_dict(self, texel):
    #    r = dict(cls=texel.__class__.__name__)
    #    r.update(texel.__dict__)
    #    return r
    
    def handle_LineColor(self, texel):
        return [dict(cls=texel.__class__.__name__, color=texel.color)]

    def handle_LineWidth(self, texel):
        return [dict(cls=texel.__class__.__name__, width=texel.width)]

    def handle_LineDashes(self, texel):
        return [dict(cls=texel.__class__.__name__, dashes=texel.dashes)]

    def handle_LineJoin(self, texel):
        return [dict(cls=texel.__class__.__name__, join_style=texel.join_style)]

    def handle_LineCap(self, texel):
        return [dict(cls=texel.__class__.__name__, cap_style=texel.cap_style)]

    def handle_FillColor(self, texel):
        return [dict(cls=texel.__class__.__name__, color=texel.color)]
    
    def handle_Line(self, texel):
        return [dict(cls=texel.__class__.__name__, points=texel.points)]

    def handle_Polygon(self, texel):
        return [dict(cls=texel.__class__.__name__, points=texel.points)]

    def handle_Path(self, texel):
        return [dict(cls=texel.__class__.__name__, data=texel.data)]

    def handle_Circle(self, texel):
        return [dict(cls=texel.__class__.__name__, x=texel.x, y=texel.y, r=texel.r)]

    def handle_Ellipse(self, texel):
        return [dict(cls=texel.__class__.__name__, x=texel.x, y=texel.y,
                     r1=texel.r1, r2=texel.r2)]

    def handle_Arc(self, texel):
        return [dict(cls=texel.__class__.__name__, x=texel.x, y=texel.y,
                     r=texel.r, start=texel.start, end=texel.end)]

    def handle_Rectangle(self, texel):
        return [dict(cls=texel.__class__.__name__, x1=texel.x1, y1=texel.y1,
                     x2=texel.x1, y2=texel.y2)]

    def handle_Font(self, texel):
        return [dict(cls=texel.__class__.__name__, size=texel.size, family=texel.family,
                     style=texel.style, weight=texel.weight, underline=texel.underline,
                     encoding=texel.encoding)]
        
    def handle_GraphicsText(self, texel):
        return [dict(cls=texel.__class__.__name__, text=texel.text, point=texel.point,
                     align=texel.align)]

    def handle_Translate(self, texel):
        return [dict(cls=texel.__class__.__name__, offset=texel.offset)]

    def handle_Rotate(self, texel):
        return [dict(cls=texel.__class__.__name__, angle=texel.angle)]

    def handle_Scale(self, texel):
        return [dict(cls=texel.__class__.__name__, fx=texel.fx, fy=texel.fy)]
    
    ### textmodel
    def handle_TextModel(self, textmodel):
        return dict(
            cls='TextModel',
            data=self.process(textmodel.texeltree)
        )

    
"""
  def undump_obj(self, dumper, s): return self.Class_new(self.Class)
  
  def undump_data(self, obj, dumper, s):
    if self.Class_setstate: self.Class_setstate(obj, dumper.undump_ref(s))
    else:                   obj.__dict__ =           dumper.undump_ref(s)
"""

    
def as_simple(texel):
    return _TexelProcessor(texel).result


    
registry = dict()


def _b64(s):
    if type(s) is list:
        s = ''.join(s)
    return b64encode(s.encode('latin-1'))


def _extract_dataobj(obj):
    """extract a data object from json obj. Data objects are all
    objects which are no texels. Currently this are only graphics
    objects (Line, Circle, ...)"""
    
    if not type(obj) is dict:
        raise SyntaxError('Expected an object: %s' % obj)
    d = obj
    cls = d['cls']
    if cls == 'Line':
        points = _extract_pylist(d['points'])
        return Line(*points)
    elif cls == 'LineColor':
        return LineColor(d['color'])
    elif cls == 'LineWidth':
        return LineWidth(d['width'])
    elif cls == 'LineDashes':
        return LineDashes(d['dashes'])
    elif cls == 'LineJoin':
        return LineJoin(d['join_style'])
    elif cls == 'LineCap':
        return LineCap(d['cap_style'])
    elif cls == 'FillColor':
        return FillColor(d['color'])
    elif cls == 'line':
        return Line(*d['points'])
    elif cls == 'Polygon':
        return Line(*d['points'])
    elif cls == 'Path':
        return Path(*d['data'])
    elif cls == 'Circle':
        return Circle((d['x'], d['y']), d['r'])
    elif cls == 'Ellipse':
        return Ellipse((d['x'], d['y']), d['r1'], d['r2'])
    elif cls == 'Arc':
        return Arc((d['x'], d['y']), d['r'], d['start'], d['end'])
    elif cls == 'Rectangle':
        return Rectangle((d['x1'], d['y1']), (d['x2'], d['y2']))
    elif cls == 'Font':
        return Font(d['size'], d['family'], d['style'], d['weight'],
                    d['underline'], d['face'], d['encoding'])
    elif cls == 'GraphicsText':
        return GraphicsText(_extract_string(d['text']), d['point'], d['align'])
    elif cls == 'Translate':
        return Translate(d['offset'])
    elif cls == 'Rotate':
        return Rotate(d['angle'])
    elif cls == 'Scale':
        return Scale(d['fx'], d['fy'])
    elif cls == "BitmapRGB":
        return BitmapRGB(size=d['size'], data=_b64(d['data']))    
    elif cls == "BitmapRGBA":
        return BitmapRGBA(size=d['size'], data=_b64(d['data']),
                          alpha=_b64(d['alpha']))    
    raise Exception("Don't know how to load object:", obj)


def _extract_graphicsobjects(obj):
    """Extract a list of graphicsobjects"""
    if not type(obj) is list:
        raise SyntaxError('Expected a list of graphics objects: %s' % obj)
    r = []
    for x in obj:
        r.append(_extract_dataobj(x))
    return r
    
            
def _extract_texel(obj, state):
    """Extract a single texel from a json object"""
    if type(obj) is list:
        l = []
        for elem in obj:
            if type(elem) is dict and 'cmd' in elem:
                _eval_cmd(elem, state)
            else:
                l.append(_extract_texel(elem, state))
        return grouped(l)

    if type(obj) is str:
        return Text(obj, style=state.current_style)
    
    # if it is not a list and not a string, obj must be a dict
    if not type(obj) is dict:
        raise SyntaxError(
            'Expected a single text element or a list of text elements, got: %s' \
            % repr(obj))
    
    d = obj
    cls = d['cls']
    if cls == "Text":
        return Text(d['text'], style=state.current_style)
    
    elif cls == "NewLine":
        return NewLine(style=state.current_style,
                       parstyle=state.current_parstyle)
    
    elif cls == "TextCell":
        text = _extract_texel(d['text'], state)
        return TextCell(text)
    
    elif cls == "ScriptingCell":
        input = _extract_texel(d['input'], state)
        output = _extract_texel(d['output'], state)            
        return ScriptingCell(input, output)
    
    elif cls == "BitmapRGB":
        return BitmapRGB(size=d['size'], data=_b64(d['data']))
    
    elif cls == "BitmapRGBA":
        return BitmapRGBA(size=d['size'], data=_b64(d['data']),
                          alpha=_b64(d['alpha']))
    
    elif cls == "Graphics":
        items = _extract_graphicsobjects(d['items'])
        return Graphics(items, size=d['size'], frame=d['frame'])
    
    else:
        raise Exception("Expected texel, not", obj)

    
def _extract_pydict(obj): # currently not needed
    """Extract a python dictionary from a json-dict."""
    r = dict()
    for key, value in obj.items():
        r[key] = _extract_basic(value)         
    return r


def _extract_pylist(obj):
    """Extract a list of basic python objects from a json-dict."""
    r = []
    for item in obj:
        r.append(_extract_basic(item))
    return r


basic_types = int, float, str, list, tuple
def _extract_basic(obj):
    """Extract a basic python type from a json object."""
    if not type(obj) in basic_types:
        raise Exception("Basic type (int float, string, list, tuple) expected", obj)
    return obj


def _eval_cmd(obj, state):
    """Evaluate a json object as command."""
    if not type(obj) is dict:
        raise SyntaxError(obj)
    cmd = obj['cmd']
    d = obj
    if cmd == 'newstyle':
        style = d.copy()
        name = style['name']
        del style['name']
        state.defined_styles[name] = style
        state.current_style = style

    elif cmd == 'style':
        name = d['name']
        style = state.defined_styles[name]
        state.current_style = style

    elif cmd == 'newparstyle':
        parstyle = d.copy()
        name = parstyle['name']
        del parstyle['name']
        state.defined_parstyles[name] = parstyle
        state.current_parstyle = parstyle

    elif cmd == 'parstyle':
        name = d['name']
        parstyle = state.defined_parstyles[name]
        state.current_parstyle = parstyle

    else:
        raise Exception('Unknown command %s' % cmd)

    
def from_simple(obj):
    class state:
        current_style = {}
        defined_styles = {}
        current_parstyle = {}
        defined_parstyles = {}

    return _extract_texel(obj, state)


def dumps(model):
    simple = as_simple(model.texel)
    return magic+json.dumps(simple, indent=2)


def loads(s):
    n = len(magic)
    if not s.startswith(magic):
        raise('Not a pynotebook-file:', repr(s[:n]))
    model = TextModel()
    simple = json.loads(s[n:])
    model.texel = from_simple(simple)
    return model


def test_00():
    model = TextModel('')
    tmp = TextModel(u'for a in range(5):\n    print a')
    cell = ScriptingCell(tmp.texel, NULL_TEXEL)
    model.insert(len(model), mk_textmodel(cell))
    model.insert(len(model), mk_textmodel(cell))
    #print(as_simple(model.texel))

    import json
    print(json.dumps(as_simple(model.texel), indent=2))


def test_01():
    import wx
    app = wx.App()
    from pynotebook.nbview import NBView
    from pynotebook.graphics import register_classes
    register_classes()
    f = wx.Frame(None)
    v = NBView(f, filename='pnb/demo/graphics.pnb')
    model = v.model
    assert len(model)>1000

    s = dumps(model)
    #print(s)
    clone = loads(s)
    assert len(model) == len(clone)
    
