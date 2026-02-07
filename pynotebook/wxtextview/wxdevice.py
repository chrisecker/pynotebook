# -*- coding: latin-1 -*-

# WxDevice provides a lightweight abstraction layer that keeps
# wx-specific code isolated from the rest of the codebase. All pixel
# coordinates are based on an assumed 96 DPI.


import wx
import time

defaultstyle = dict(
    fontsize=10, bgcolor='white', textcolor='black', 
    underline=False, facename='', italic=False, bold=False)


def filled(style, defaultstyle=defaultstyle):
    # fill empty properties with default values
    new = defaultstyle.copy()
    new.update(style)
    return new


def get_font(style):
    weight = {False : wx.FONTWEIGHT_NORMAL,
              True : wx.FONTWEIGHT_BOLD}[style.get('bold', False)]
    slant = {False : wx.FONTSTYLE_NORMAL,
              True : wx.FONTSTYLE_ITALIC}[style.get('italic', False)]

    family = dict(
        roman = wx.FONTFAMILY_ROMAN,
        modern = wx.FONTFAMILY_MODERN, 
        swiss = wx.FONTFAMILY_SWISS,        
    )[style.get('family', 'modern')]
    return wx.Font(
        style['fontsize'], family, slant, weight,
        style['underline'], style['facename'])

def get_font_scaled(style, factor):
    # return font scale by factor
    weight = {False : wx.FONTWEIGHT_NORMAL,
              True : wx.FONTWEIGHT_BOLD}[style.get('bold', False)]
    slant = {False : wx.FONTSTYLE_NORMAL,
              True : wx.FONTSTYLE_ITALIC}[style.get('italic', False)]

    family = dict(
        roman = wx.FONTFAMILY_ROMAN,
        modern = wx.FONTFAMILY_MODERN, 
        swiss = wx.FONTFAMILY_SWISS,        
    )[style.get('family', 'modern')]
    return wx.Font(
        style['fontsize']*factor, family, slant, weight,
        style['underline'], style['facename'])


# Profiling revelead that a lot of time is spent in the measure_*
# functions. We therefore cache the results in a fixed size dict. This
# reduces the time spent by ~90%.
_cache = dict()
_cache_keys = []



class WxDevice:
    PX_PER_PT = 96 / 72  # MemoryDC assumes 96 DPI
    SCALE = 16
    SCALE = 1 # Factor for subpixel accuracy
    buffering = True
    def __init__(self):
        # persistent MemoryDC
        self._bmp = wx.Bitmap(1 * self.SCALE, 1 * self.SCALE)
        self._dc = wx.MemoryDC(self._bmp)

        self._cache = {}
        self._cache_keys = []
        self._cache_max = 1000

    def init_dc(self, dc):
        pass
        
    def intersects(self, dc, rect):
        x1, y1, x2, y2 = rect.items()
        r = wx.Rect(int(x1), int(y1), int(x2-x1), int(y2-y1))
        return dc.ClippingRect.Intersects(r)

    def draw_text(self, text, x, y, dc):
        dc.DrawText(text, int(x), int(y))

    def draw_blinkingrect(self, x, y, w, h, dc):
        if int(time.time()*2) % 2:
            dc.SetBrush(wx.BLACK_BRUSH)
        else:
            dc.SetBrush(wx.LIGHT_GREY_BRUSH)            
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(int(x), int(y), int(w), int(h))

    def draw_rect(self, x, y, w, h, dc):
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.BLACK_PEN)
        dc.DrawRectangle(int(x), int(y), int(w), int(h))
        
    def measure(self, text, style):
        """
        Measure text width/height in pt as float with subpixel accuracy
        """
        key = (text, tuple(sorted(style.items())))
        try:
            return self._cache[key]
        except KeyError:
            pass
        style_filled = filled(style)

        text_clean = text.replace("\n", " ")
        font = get_font_scaled(style_filled, self.SCALE)
        self._dc.SetFont(font)

        # Measure in "high-resolution pixels"
        w, h = self._dc.GetTextExtent(text_clean)

        # Convert px -> pt
        f = 1/self.SCALE

        # Cache
        r = f*w, f*h
        self._cache[key] = r
        self._cache_keys.insert(0, key)
        if len(self._cache_keys) > self._cache_max:
            old_key = self._cache_keys.pop()
            del self._cache[old_key]
        return r
    
    def measure_parts(self, text, style):
        style = filled(style)
        font = get_font_scaled(style, self.SCALE)
        self._dc.SetFont(font)
        f = 1/self.SCALE
        l = self._dc.GetPartialTextExtents(text)
        return [f*x for x in l]

    def invert_rect(self, x, y, w, h, dc):
        # wx phoenix does not seem to support xor or invert. As an
        # alternative we draw a semitransparent blue Box above the rect.
        #brush = wx.Brush((0, 0, 250, 50), style=wx.BRUSHSTYLE_SOLID)
        brush = wx.Brush((83, 97, 220, 50), style=wx.BRUSHSTYLE_SOLID)
        #brush = wx.Brush(wx.Colour(255, 255, 255, 80)) 
        dc.SetBrush(brush)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(int(x), int(y), int(w), int(h))

    def set_style(self, style, dc):
        if hasattr(dc, 'last_style') and  style is dc.last_style:
            return
        dc.last_style = style

        _style = filled(style)
        font = get_font(_style)
        dc.SetFont(font)            
        dc.SetTextBackground(wx.Colour(_style['bgcolor']))
        dc.SetTextForeground(wx.Colour(_style['textcolor']))
        


# XXX nicht mehr gebraucht!
class DCStyler:
    last_style = None
    def __init__(self, dc):
        self.dc = dc
        
    def set_style(self, style):
        if style is self.last_style:
            return
        self.last_style = style

        _style = filled(style)
        font = get_font(_style)
        self.dc.SetFont(font)            
        try: # Phoenix
            self.dc.SetTextBackground(wx.Colour(_style['bgcolor']))
            self.dc.SetTextForeground(wx.Colour(_style['textcolor']))
        except TypeError: # Classic
            self.dc.SetTextBackground(wx.NamedColour(_style['bgcolor']))
            self.dc.SetTextForeground(wx.NamedColour(_style['textcolor']))



### The following functions are here for historic reasons. I assume
### that they are not necessary anymore.

def invert_rect_INV(self, x, y, w, h, dc):
    if 1:
        dc.SetLogicalFunction(wx.INVERT)
        dc.SetBrush(wx.BLACK_BRUSH)
        dc.SetPen(wx.TRANSPARENT_PEN)
    else:
        # Alternative which gives a light blue selection: 
        dc.SetLogicalFunction(wx.XOR)
        dc.SetBrush(wx.RED_BRUSH)
    dc.DrawRectangle(int(x), int(y), int(w), int(h))


            
def invert_rect_BLIT(self, x, y, w, h, dc):
    dc.Blit(x, y, w, h, dc, x, y, wx.SRC_INVERT)


def measure_win(self, text, style):
    key = text, tuple(style.items())
    try:
        return _cache[key]
    except:
        pass
    style = filled(style)
    font = get_font(style)
    dc = wx.MemoryDC()
    dc.SetFont(font)
    w, h = dc.GetTextExtent(text)
    _cache[key] = w, h
    _cache_keys.insert(0, key)
    if len(_cache_keys) > 1000:
        _key = _cache_keys.pop()
        del _cache[key]        
    return w, h

def measure_mac(self, text, style):
    key = text, tuple(style.items())
    try:
        return _cache[key]
    except:
        pass
    style = filled(style)
    font = get_font(style)
    gc = wx.GraphicsContext_CreateMeasuringContext()
    gc.SetFont(font)
    w, h = gc.GetTextExtent(text)
    _cache[key] = w, h
    _cache_keys.insert(0, key)
    if len(_cache_keys) > 1000:
        _key = _cache_keys.pop()
        del _cache[key]        
    return w, h

def measure_gtk(self, text, style):
    key = text, tuple(style.items())
    try:
        return _cache[key]
    except:
        pass
    style = filled(style)
    text = text.replace('\n', ' ') # replace newlines to avoid double lines
    font = get_font(style)
    # GC returns wrong font metric values in gtk! We therefore use the DC.  
    dc = wx.MemoryDC()
    dc.SetFont(font)
    w, h = dc.GetTextExtent(text)
    _cache[key] = w, h
    _cache_keys.insert(0, key)
    if len(_cache_keys) > 1000:
        _key = _cache_keys.pop()
        del _cache[key]        
    return w, h


def measure_parts_win(self, text, style):
    style = filled(style)
    font = get_font(style)
    dc = wx.MemoryDC()
    dc.SetFont(font)
    return dc.GetPartialTextExtents(text)


def measure_parts_gtk(self, text, style):
    style = filled(style)
    font = get_font(style)
    dc = wx.MemoryDC()
    dc.SetFont(font)
    return dc.GetPartialTextExtents(text)


def measure_parts_mac(self, text, style):
    style = filled(style)
    font = get_font(style)
    gc = wx.GraphicsContext_CreateMeasuringContext()
    gc.SetFont(font)
    return gc.GetPartialTextExtents(text)



def test_00():
    def view(dc):
        frame = wx.Frame(parent=None, title='Hello World')
        frame.Show()
        b = wx.Button(frame)           
        bmp = dc.GetAsBitmap()
        b.SetBitmap(bmp) 
        app.MainLoop()

    def prepare_dc():
        dc = wx.MemoryDC()    
        bmp = wx.Bitmap(100, 200)
        dc.SelectObject(bmp)

        b = wx.Brush(wx.Colour(255, 0, 0)) 
        dc.SetBrush(b) 
        dc.DrawCircle(100, 100, 50)
        return dc
        
    import wx
    app = wx.App()
    device = WxDevice()
    
    dc = prepare_dc()
    device.invert_rect(10, 10, 80, 80, dc)
    #view(dc)

    # just check that this does not give an exception
    print(device.measure("asdasd", defaultstyle))

    # just check that this does not give an exception
    print(device.measure_parts("asdasd", defaultstyle))

