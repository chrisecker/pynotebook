# -*- coding: latin-1 -*-


import wx
from .nbtexels import TextCell, NotFound
from .textmodel.textmodel import TextModel
from .textmodel.viewbase import ViewBase
from .textmodel.texeltree import EMPTYSTYLE, provides_childs, iter_childs, \
    NewLine, dump
from .textmodel.styles import create_style, updated_style
from .wxtextview.wxdevice import defaultstyle



class ColourButton(wx.Button):
    """3 state color button"""
    callback = None
    def __init__(self, parent, size=(100,30)):
        super().__init__(parent, label="", size=size)
        self.colour = None # initial color
        self.Bind(wx.EVT_BUTTON, self.on_click)
        self.update_bitmap()

    def on_click(self, event):
        cd = wx.ColourData()
        cd.SetColour(self.colour)
        dlg = wx.ColourDialog(self, cd)
        if dlg.ShowModal() == wx.ID_OK:
            self.set_colour(dlg.GetColourData().GetColour())
            if self.callback:
                self.callback()
        dlg.Destroy()

    def set_colour(self, colour):
        self.colour = colour
        self.update_bitmap()
        
    def update_bitmap(self):
        w, h = self.GetSize()
        bmp = wx.Bitmap(w, h)
        dc = wx.MemoryDC(bmp)

        if self.colour is None:
            # Mixed-State: diagonalen Streifen auf weiße Hintergrund
            dc.SetBackground(wx.WHITE_BRUSH)
            dc.Clear()
            brush = wx.Brush(wx.BLACK, wx.BRUSHSTYLE_BDIAGONAL_HATCH)            
        else:
            brush = wx.Brush(self.colour)

        dc.SetPen(wx.Pen("black", 5))
        dc.SetBrush(brush)
        dc.DrawRectangle(0, 0, w, h)

        dc.SelectObject(wx.NullBitmap)
        self.SetBitmap(bmp)


        
class ResetButton(wx.Button):
    callback = None
    def __init__(self, parent, properties):
        super().__init__(parent, label="", size=(24, 24), style=wx.BORDER_NONE)
        self.properties = properties
        self.SetForegroundColour(wx.Colour(200, 0, 0))
        self.SetToolTip("Remove local change")
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.on_button)

    def on_button(self, event):
        if self.callback:
            self.callback(self.properties)

    def set_x(self, visible: bool):
        if visible == self.Enabled:
            return
        if visible:
            self.SetLabel("\u2715")
            self.Enable()
        else:
            self.SetLabel("")   # no X
            self.Disable()      # not clickable

            
            
class Inspector(wx.Frame, ViewBase):
    sizes = (8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 30)
    def __init__(self, view, parent, *args, **kwds):
        ViewBase.__init__(self)
        wx.Frame.__init__(self, parent, *args, title='Format',
                          style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT
                          |wx.FRAME_TOOL_WINDOW, **kwds)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy)
        
        framesizer = wx.BoxSizer( wx.VERTICAL )
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        self.SetBackgroundColour(panel.BackgroundColour)
        
        panelsizer = wx.BoxSizer(wx.VERTICAL)
        self.basestyle = wx.Choice(panel)
        self.basestyle.Bind(wx.EVT_CHOICE, self.on_basestyle)
        panelsizer.Add(self.basestyle, 0, wx.ALL|wx.EXPAND, 5)

        line = wx.StaticLine(panel, style=wx.LI_HORIZONTAL)
        panelsizer.Add(line, 0, wx.ALL, 5)

        
        contentsizer = wx.BoxSizer(wx.VERTICAL)
        choices = list(map(str, self.sizes))

        self.size = wx.ComboBox(
            panel, value = "12", choices=choices,
            style = wx.CB_DROPDOWN| wx.TE_PROCESS_ENTER
        )
        self.reset_size = ResetButton(panel, ['fontsize'])
        self.size.SetMinSize((100, -1))

        ALL_CENTER = wx.ALL|wx.ALIGN_CENTER_VERTICAL

        rowsizer = wx.BoxSizer(wx.HORIZONTAL)
        rowsizer.Add(self.size, 1, wx.ALL, 5)
        rowsizer.Add(self.reset_size, 0, ALL_CENTER, 5)
        contentsizer.Add(rowsizer, 0, wx.EXPAND) 
        
        for binder in wx.EVT_TEXT_ENTER, wx.EVT_KILL_FOCUS, wx.EVT_COMBOBOX:
            self.size.Bind(binder, self.on_size)

        self.textcolor = ColourButton(panel)
        self.bgcolor = ColourButton(panel)
        self.reset_colors = ResetButton(panel, ['textcolor', 'bgcolor'])
        
        rowsizer = wx.BoxSizer(wx.HORIZONTAL)
        rowsizer.Add(self.textcolor, 1, wx.ALL, 5)
        rowsizer.Add(self.bgcolor, 1, wx.ALL, 5)
        rowsizer.Add(self.reset_colors, 0, ALL_CENTER, 5)
        contentsizer.Add(rowsizer, 0, wx.EXPAND) 
        
        self.textcolor.callback = lambda: self.set_properties(
                textcolor=self.textcolor.colour.GetAsString())

        self.bgcolor.callback = lambda: self.set_properties(
                bgcolor=self.bgcolor.colour.GetAsString())

        self.underline = wx.CheckBox(panel, -1, "Underline",
                                     style=wx.CHK_3STATE)
        self.reset_underline = ResetButton(panel, ['underline'])
        rowsizer = wx.BoxSizer(wx.HORIZONTAL)
        rowsizer.Add(self.underline, 0, wx.ALL, 5)
        rowsizer.Add(self.reset_underline, 0, ALL_CENTER, 5)
        contentsizer.Add(rowsizer, 0)
        
        self.underline.Bind(
            wx.EVT_CHECKBOX,
            lambda e:self.set_properties(underline=self.underline.GetValue()))

        self.bold = wx.CheckBox(panel, -1, "Bold", style=wx.CHK_3STATE)
        self.reset_bold = ResetButton(panel, ['bold'])
        rowsizer = wx.BoxSizer(wx.HORIZONTAL)
        rowsizer.Add(self.bold, 0, wx.ALL, 5)
        rowsizer.Add(self.reset_bold, 0, ALL_CENTER, 5)
        contentsizer.Add(rowsizer, 0)
        
        self.bold.Bind(
            wx.EVT_CHECKBOX,
            lambda e:self.set_properties(bold=self.bold.GetValue()))

        self.italic = wx.CheckBox(panel, -1, "Italic", style=wx.CHK_3STATE)
        self.reset_italic = ResetButton(panel, ['italic'])
        rowsizer = wx.BoxSizer(wx.HORIZONTAL)
        rowsizer.Add(self.italic, 0, wx.ALL, 5)
        rowsizer.Add(self.reset_italic, 0, ALL_CENTER, 5)
        contentsizer.Add(rowsizer, 0)

        self.italic.Bind(
            wx.EVT_CHECKBOX,
            lambda e:self.set_properties(italic=self.italic.GetValue()))

        button = wx.Button(panel, -1, "Clear")
        button.Bind(wx.EVT_BUTTON, self.on_clear)
        contentsizer.Add( button, 0, wx.ALL, 5 )

        panelsizer.Add(contentsizer, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(panelsizer )
        panel.Layout()
        panelsizer.Fit(panel )
        framesizer.Add(panel, 1, wx.EXPAND |wx.ALL, 5)

        self.SetSizer( framesizer )
        self.Layout()
        framesizer.Fit(self)

        for resetter in [
                self.reset_colors,
                self.reset_size,
                self.reset_underline,
                self.reset_bold,
                self.reset_italic]:
            resetter.callback = self.reset_cb

        self.add_model(view)
        model = view.model
        assert model is not None
        self.add_model(view.model)

        
    def on_destroy(self, event):
        self.destroy()

    def model_changed(self, *args):
        self.update()
        
    def reset_cb(self, keys):
        self.clear_properties(*keys)

    def on_clear(self, event):
        textview = self.model
        i1, i2 = sorted(textview.selection)
        textview.clear_styles(i1, i2)

    def on_size(self, event=None):
        try:
            fontsize=int(self.size.GetValue())
        except ValueError:
            return self.update()
        # NOTE: wxdevice only allows integer fontsizes!
        self.set_properties(fontsize=fontsize)

    def on_face(self, event=None):
        i = self.fontface.Selection
        facename = self.faces[i]
        self.set_properties(facename = facename)

    def on_basestyle(self, event=None):
        textview = self.model
        textmodel = textview.model
        i1, i2  = sorted(textview.selection)

        # inefficient way to find the next NL
        row, col = textmodel.index2position(i2)
        tmp = textmodel.lineend(row)
        i2 = tmp+1 # the newline is always at lineend..lineend+1 (even
                   # for ENDMARK!)
        stylesheet = textview.builder.stylesheet
        i = self.basestyle.Selection
        name = self._stylenames[i]
        textview.set_parproperties(i1, i2, base=name)
        
    def set_properties(self, **properties):        
        textview = self.model
        if not textview.has_selection():
            return
        i1, i2  = sorted(textview.selection)
        textview.set_properties(i1, i2, **properties)

    def clear_properties(self, *keys):
        textview = self.model
        if not textview.has_selection():
            return
        i1, i2  = sorted(textview.selection)
        textview.clear_properties(i1, i2, *keys)

    def mk_style(self, parstyle, style):
        # Computes the style of a single run of text. Unlike the code
        # in nbview, we aggregate parstyle and textstyles. This way,
        # we can use the same code for paragraph and text
        # styles. Further we include defaultstyles which is not done
        # in nbviews (but in wxdevice).
        stylesheet = self.model.builder.stylesheet
        basestyle = stylesheet[parstyle.get('base', 'normal')]
        r = updated(defaultstyle, basestyle, parstyle, style)
        if not 'base' in r:
            r['base'] = 'normal'
        return r
    _stylenames = ()
    def update(self, event=None):
        textview = self.model
        textmodel = textview.model
        
        # Update list of basestyles:
        stylesheet = textview.builder.stylesheet
        stylenames = sorted(stylesheet.keys())
        if stylenames != self._stylenames:            
            self.basestyle.SetItems(stylenames)
            self._stylenames = stylenames
        
        index = textview.index
        if textview.has_selection():
            s1, s2 = sorted(textview.selection)
            properties, overrides = collect_properties(
                textmodel, s1, s2, self.mk_style)            
        else:
            style = textmodel.get_style(max(0, index-1))
            parstyle = textmodel.get_parstyle(index)
            properties = self.mk_style(parstyle, style)
            overrides = set(style.keys())

        #print("overrides", overrides)
        #print("properties", properties)

        base = properties.get('base', 'normal')
        if base is not None:
            i = self._stylenames.index(base)
            self.basestyle.SetSelection(i)
        else:
            self.basestyle.SetSelection(-1)
                                  
        self.textcolor.set_colour(properties['textcolor'])
        self.bgcolor.set_colour(properties['bgcolor'])
        x = 'textcolor' in overrides or 'bgcolor' in overrides
        self.reset_colors.set_x(x)
            
        checkboxes_names = "underline italic bold".split()
        for name in checkboxes_names:
            widget = getattr(self, name)
            reset = getattr(self, 'reset_'+name)
            reset.set_x(name in overrides)
            value = properties[name]
            if value is None:
                widget.Set3StateValue(wx.CHK_UNDETERMINED)
            else:
                widget.SetValue(value)

        size = properties['fontsize']
        if size is None:
            self.size.SetValue('')
        else:
            self.size.SetValue(str(size))
        x = 'fontsize' in overrides
        self.reset_size.set_x(x)
        

        
class TextCellInspector(Inspector):
    # Inspector which is only enabled when the cursor is in a text
    # cell.
    def update(self, event=None):
        textview = self.model
        try:
            i, cell = textview.find_cell()
        except NotFound:
            cell = None
        is_textcell = isinstance(cell, TextCell)
        Inspector.update(self)
        self.Enable(is_textcell)


        
def _collect_properties(texel, i1, i2, parstyle, mk_style):
    """Gibt ein Dict mit Properties zurück (values sind None wenn
    uneindeutig) und ein Set mit override den überschriebenen
    Properties.

    """
    if provides_childs(texel):
        properties = dict()
        overrides = set()
        
        for j1, j2, child in reversed(list(iter_childs(texel))):
            if i1 < j2 and j1 < i2: # overlapp
                s, o, parstyle = _collect_properties(child, i1-j1, i2-j1, parstyle,
                                                     mk_style)
                overrides.update(o)
                for key, value in s.items():
                    if not key in properties:
                        properties[key] = value
                    elif properties[key] != value:
                        properties[key] = None
    else:
        #print("texel:", texel)
        if isinstance(texel, NewLine):
            parstyle = texel.parstyle
        s = texel.style
        overrides = set(s.keys()).union(parstyle.keys())
        properties = mk_style(parstyle, s)        
    return properties, overrides, parstyle


def updated(default, *styles):
    """Merges dicts by updating from left to right."""    
    r = default.copy()
    for s in styles:
        r.update(s)
    return r


def _mk_style(parstyle, style):
    # Simplified style-model. For testing only.
    return updated(parstyle, style)


def collect_properties(model, i1, i2, mk_style=_mk_style):
    parstyle = model.get_parstyle(i2)
    return _collect_properties(model.get_xtexel(), i1, i2, parstyle,
                               mk_style)[:2]
                        

def mk_demo(redirect=False):
    from .nbview import NBView    
    from .nbtexels import TextCell, NULL_TEXEL, mk_textmodel, TextModel
    from .textmodel.texeltree import T
    
    app = wx.App(redirect=redirect)
    frame = wx.Frame(None)
    win = wx.Panel(frame)
    view = NBView(win)
    model = TextModel(u"Some\ntext\n...")
    model.set_properties(1, 5, textcolor='red')
    text = model.texel
    cell = TextCell(text)
    view.model.insert(0, mk_textmodel(cell))
    box = wx.BoxSizer(wx.VERTICAL)
    box.Add(view, 1, wx.ALL|wx.GROW, 1)
    win.SetSizer(box)
    win.SetAutoLayout(True)
    win.Show()
    frame.Show()    
    return app, view, model
    
def demo_00():
    app, view, model = mk_demo(redirect=True)
    inspector = TextCellInspector(view, None)
    inspector.Show()
    if 1:
        from pynotebook.wxtextview import testing
        l = locals()
        l.update(globals())
        testing.pyshell(l)

    app.MainLoop()



def test_00():
    "get_parstyle" # just to be sure
    m = TextModel("Eins\nZwei\ndrei")
    m.set_parstyle(0, dict(x=1)) # -> Parstyle für "Eins\n"
    m.set_parstyle(5, dict(x=2)) # -> Parstyle für "Zwei\n"
    assert m.get_parstyle(0)['x'] == 1 # E
    assert m.get_parstyle(1)['x'] == 1 # i
    assert m.get_parstyle(2)['x'] == 1 # n
    assert m.get_parstyle(3)['x'] == 1 # s
    assert m.get_parstyle(4)['x'] == 1 # \n
    assert m.get_parstyle(5)['x'] == 2 # Z
    assert m.get_parstyle(6)['x'] == 2 # w
    
def test_01():
    "collect styles"
    
    m = TextModel("Eins\nZwei\ndrei")
    m.set_parstyle(0, dict(x=1)) # -> Parstyle für "Eins\n"
    m.set_parstyle(5, dict(x=2)) # -> Parstyle für "Zwei\n"
    m.set_parstyle(11, dict(x=3)) # -> Parstyle für "Drei\n"
    #dump(m.get_xtexel())

    assert collect_properties(m, 1, 3) == ({'x': 1}, set())
    # base style is not overriden

    m.set_properties(1, 2, x=99)
    assert collect_properties(m, 1, 3) == ({'x': None}, set('x'))
    # base style is overriden, multiple values for 'x'

    m.set_properties(1, 4, x=99)
    
    assert collect_properties(m, 1, 3) == ({'x': 99}, set('x'))
    # base style is overriden, single value

    assert collect_properties(m, 1, 4) == ({'x': 99}, set('x'))
    # base style is overriden, single value

    assert collect_properties(m, 1, 5) == ({'x': None}, set('x'))
    # base style is overriden, multiple values

    assert collect_properties(m, 5, 7) == ({'x': 2}, set())
    # base style is not overriden, single values

    assert collect_properties(m, 4, 7) == ({'x': None}, set())
    # base style is not overriden, multiple values

    
def test_02():
    app, view, model = mk_demo()
    inspector = TextCellInspector(view, None)

    view.index = 3
    view.selection = 1, 3
    
    


    
    
