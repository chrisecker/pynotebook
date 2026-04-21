# -*- coding: utf-8 -*-


from .textmodel.textmodel import TextModel, dump_range
from .textmodel.texeltree import Texel, T, G, NL, Container, Single, \
    iter_childs, dump, NULL_TEXEL, length, grouped, copy

import wx
import base64    
import io



def mk_textmodel(texel):
    model = TextModel()
    model.texel = texel
    return model



class Cell(Container):
    pass


class TextCell(Cell):
    text = property(lambda s:s.childs[1])
    def __init__(self, text, **kwargs):
        assert isinstance(text, Texel)
        self.childs = [NL, text, NL]
        self.compute_weights()



class ScriptingCell(Cell):

    client_name = 'python'

    input = property(lambda s:s.childs[1])
    output = property(lambda s:s.childs[3])

    def __init__(self, input, output, number = 0, **kwargs):
        assert isinstance(input, Texel)
        assert isinstance(output, Texel)
        self.number = number
        self.childs = [NL, input, NL, output, NL]
        self.compute_weights()


def strip_output(texel):
    if isinstance(texel, ScriptingCell):
        clone = texel.__class__(texel.input, NULL_TEXEL)
        return clone
    elif texel.is_group:
        r = []
        for child in texel.childs:
            r.append(strip_output(child))
        return G(r)
    else: 
        return texel


def _split_cell(texel, i):
    if i<=0 or i>=length(texel): return [texel]
    if texel.is_group:
        r = []
        for i1, i2, child in iter_childs(texel):
            if i1<i<i2:
                r.append(split_cell(child, i-i1))
            else:
                r.append(child)
        return r
    if isinstance(texel, Cell):
        r1 = []
        r2 = []
        for i1, i2, child in iter_childs(texel):
            if i1<i<i2:
                j = i-i1
                r1.append(grouped(copy(child, 0, j)))
                r2.append(grouped(copy(child, j, i2-i1)))
            else:
                r1.append(child)
                r2.append(child)
        return [strip_output(texel.set_childs(r1)),
                texel.set_childs(r2)]        
    return [texel]

def split_cell(texel, i):
    return grouped(_split_cell(texel, i))


class NotFound(Exception): pass

def find_cell(texel, i, i0=0):
    if isinstance(texel, Cell):
        return i0, texel
    elif texel.is_group:
        for j1, j2, child in iter_childs(texel):
            if j1<=i<j2:
                return find_cell(child, i-j1, i0+j1)
    raise NotFound()


def _bitmap_saver(bitmap):
    # we convert images to png before saving to save disk space
    w, h = bitmap.size
    if isinstance(bitmap, BitmapRGBA):
        im = wx.Image(w, h, bitmap.data, bitmap.alpha)
    else:
        im = wx.Image(w, h, bitmap.data)
    output = io.BytesIO()
    im.SaveFile(output, wx.BITMAP_TYPE_PNG)
    return base64.b64encode(output.getvalue())



def _bitmap_loader(data):
    pngdata = base64.b64decode(data)
    stream = io.BytesIO(pngdata)
    image = wx.Image(stream, type=wx.BITMAP_TYPE_ANY)
    # Force copies: GetData/GetAlpha may return memoryviews backed by
    # the wxImage's internal buffer. Once `image` is garbage-collected
    # that memory is freed and reused, producing aliasing artifacts.
    alpha = image.GetAlpha()
    return ((image.Width, image.Height),
            bytes(image.GetData()),
            bytes(alpha) if alpha is not None else None)



class BitmapRGB(Single):
    def __init__(self, data, size):
        self.data = data
        self.size = size

    def __repr__(self):
        return 'BitmapRGB(...)'

    def __getstate__(self):
        return _bitmap_saver(self)

    def __setstate__(self, data):
        if data is not None:
            self.size, self.data = _bitmap_loader(data)[:2]

    def draw(self, gc, state):
        w, h = self.size
        bitmap = wx.BitmapFromBuffer(w, h, self.data)
        m = gc.CreateMatrix()
        gc.SetTransform(m)
        gc.ConcatTransform(state['trafo'])
        gc.ConcatTransform(state['matrix'])
        gc.DrawBitmap(bitmap, 0, 0, w, h)
        gc.SetTransform(state['trafo'])


class BitmapRGBA(Single):
    def __init__(self, data, alpha, size):
        self.data = data
        self.alpha = alpha
        self.size = size

    def __repr__(self):
        return 'BitmapRGB(...)'

    def __getstate__(self):
        return _bitmap_saver(self)

    def __setstate__(self, data):
        if data is not None:
            self.size, self.data, self.alpha = _bitmap_loader(data)

    def draw(self, gc, state):
        w, h = self.size
        im = wx.Image(w, h, self.data)
        im.SetAlphaBuffer(self.alpha)
        bitmap = wx.Bitmap(im)
        m = gc.CreateMatrix()
        gc.SetTransform(m)
        gc.ConcatTransform(state['trafo'])
        gc.ConcatTransform(state['matrix'])
        gc.DrawBitmap(bitmap, 0, 0, w, h)
        gc.SetTransform(state['trafo'])


class Graphics(Single):
    def __init__(self, item, size=(100, 100), frame=False):
        if type(item) is tuple:
            self.items = item
        elif type(item) is list:
            self.items = tuple(item)
        else:
            self.items = (item)
        self.size = size
        self.frame = frame



def test_00():
    "TextCell"
    cell = TextCell(T('0123456789'))
    model = TextModel()
    cellmodel = mk_textmodel(cell)
    model.insert(0, cellmodel)
    dump(model.texel)
    model.insert_text(4, "xyz")
    dump(model.texel)


def test_01():
    import pickle
    app = wx.App()

    im = wx.ArtProvider.GetBitmap(wx.ART_WARNING, size=(128, 128)).ConvertToImage()
    texel = BitmapRGBA(im.GetData(), im.GetAlpha(), im.GetSize())
    s = pickle.dumps(texel)
    obj = pickle.loads(s)
    s2 = pickle.dumps(obj)
    assert s == s2

    texel = BitmapRGB(im.GetData(), im.GetSize())
    s = pickle.dumps(texel)
    obj = pickle.loads(s)
    s2 = pickle.dumps(obj)
    assert s == s2


def _make_bitmap_rgba(w, h):
    # Creates BitmapRGBA from a wx.Image that immediately goes out of scope,
    # simulating the real usage in pyclient.__transform__ and _bitmap_loader.
    im = wx.ArtProvider.GetBitmap(wx.ART_WARNING, size=(w, h)).ConvertToImage()
    return BitmapRGBA(bytes(im.GetData()), bytes(im.GetAlpha()), (w, h))


def test_04():
    "Regression: wx.Image buffer reuse corrupts alpha across sequential loads"
    # wx.Image uses an internal memory pool. When the first image is freed,
    # the second wx.Image load may receive the same buffer. If GetData/GetAlpha
    # returned views (not copies), the first texel's alpha would silently
    # contain the second image's data.
    import gc
    app = wx.App()

    w, h = 8, 8
    alpha_a = bytes([200] * (w * h))
    alpha_b = bytes([100] * (w * h))
    state_a = _bitmap_saver(BitmapRGBA(bytes(range(w*h*3)),      alpha_a, (w, h)))
    state_b = _bitmap_saver(BitmapRGBA(bytes([128]*(w*h*3)), alpha_b, (w, h)))

    # Load A — keep the returned alpha alive
    _, _, a1 = _bitmap_loader(state_a)
    snapshot1 = bytes(a1)          # snapshot immediately after load
    gc.collect()

    # Load B — in the buggy version this reuses A's freed buffer
    _, _, a2 = _bitmap_loader(state_b)
    gc.collect()
    snapshot2 = bytes(a1)          # re-read A's alpha after B was loaded

    assert snapshot1 == alpha_a, f"alpha_a wrong after load: {set(snapshot1)}"
    # This assertion catches the bug: if a1 is a view into the reused buffer,
    # snapshot2 would equal alpha_b (or garbage) instead of alpha_a.
    assert snapshot2 == alpha_a, \
        f"alpha_a corrupted after loading image B: {set(snapshot2)} != {set(alpha_a)}"


def test_03():
    "BitmapRGBA: alpha and RGB survive _bitmap_saver/_bitmap_loader"
    app = wx.App()
    w, h = 8, 8
    data  = bytes(i % 256 for i in range(w * h * 3))
    alpha = bytes(128 + i % 128 for i in range(w * h))  # non-trivial, non-255 values
    texel = BitmapRGBA(data, alpha, (w, h))

    state = _bitmap_saver(texel)
    (lw, lh), ldata, lalpha = _bitmap_loader(state)

    assert (lw, lh) == (w, h), f"size mismatch: {(lw,lh)}"
    assert ldata == data,   f"RGB data corrupted in save/load"
    assert lalpha == alpha, f"alpha corrupted: {list(lalpha[:8])} != {list(alpha[:8])}"


def test_02():
    "BitmapRGBA round-trip: pixel data survives save/load (dangling-ptr regression)"
    import pickle, gc
    app = wx.App()

    # Create reference data with wx.Image out of scope
    ref = _make_bitmap_rgba(64, 64)
    ref_data = bytes(ref.data)
    ref_alpha = bytes(ref.alpha)
    gc.collect()

    # Round-trip via pickle (__getstate__ / __setstate__)
    loaded = pickle.loads(pickle.dumps(ref))
    gc.collect()

    assert loaded.size == ref.size
    assert bytes(loaded.data)  == ref_data,  "RGB data corrupted after save/load"
    assert bytes(loaded.alpha) == ref_alpha, "alpha data corrupted after save/load"

    # Second round-trip: loaded object saved again must be stable
    loaded2 = pickle.loads(pickle.dumps(loaded))
    assert bytes(loaded2.data)  == ref_data,  "RGB data corrupted on 2nd save/load"
    assert bytes(loaded2.alpha) == ref_alpha, "alpha data corrupted on 2nd save/load"
