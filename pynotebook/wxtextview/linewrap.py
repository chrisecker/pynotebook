# -*- coding: latin-1 -*-

from .testdevice import TESTDEVICE
from .boxes import TabulatorBox, TextBox, EmptyTextBox, NewlineBox, Row




def find_goodbreak(box, maxw): # currently not used!
    """Search good break position at or before maxw, returns None
       (i.e. no good split position possible) otherwise. If the
       box.width <= maxw, len(box) is returned.
    """
    if (not isinstance(box, TextBox)) or maxw <= 0:
        # no good split is possible
        return None

    if box.width<=maxw:
        # split is not necessary
        return len(box)

    text = box.text
    if not text:
        return None

    measure = box.measure
    width = 0
    ws = measure(' ')[0]
    i = 0
    for word in text.split(' '):
        w = measure(word)[0]

        if width+w <= maxw:
            i += len(word)+1
            width += w+ws
            continue
        if i==0:
            return None
        return min(len(text), i)
    return None

    
def find_anybreak(box, maxw):
    """Search possible break position at or before maxw, returns None
       otherwise.
    """
    if not isinstance(box, TextBox) or maxw <= 0:
        return None # not breakable

    parts = box.measure_parts(box.text)
    for i, part in enumerate(parts):
        if part > maxw:
            return max(i, 1)  # mindestens 1 Zeichen
    return len(parts)


def split_box(box, i):
    if not isinstance(box, TextBox):
        assert i == 0
        return EmptyTextBox(), box

    text, style, device = box.text, box.style, box.device
    return (
        box.__class__(text[:i], style, device),
        box.__class__(text[i:], style, device),
    )


def simple_linewrap(boxes, maxw, tabstops=(), wordwrap=True, device=TESTDEVICE):
    
    rows, line = [], []
    w = 0
    boxes = list(boxes)

    last_space = None  # (index_in_line, char_index)

    while boxes:
        box = boxes.pop(0)
        if not box or not len(box):
            continue

        # passt komplett?
        if w + box.width <= maxw:
            line.append(box)
            w += box.width

            if isinstance(box, TextBox) and ' ' in box.text:
                last_space = (len(line) - 1, box.text.rindex(' ') + 1)
            continue

        # Wir müssen brechen!
        
        if last_space:
            # wir brechen an dem Space
            k, j = last_space
            a, b = split_box(line[k], j)

            boxes = [b] + line[k + 1:] + [box] + boxes
            line = line[:k] + [a]
            rows.append(Row(line, device))
        else:
            # wir benutzen Gewalt
            i = find_anybreak(box, maxw-w)
            if i is None:
                # box is unsplittable!
                line.append(box)
            else:
                a, b = split_box(box, i)
                if i > 0:
                    line.append(a)
                if b:
                    boxes = [b] + boxes
            rows.append(Row(line, device))

        # neue Zeile
        line, w, last_space = [], 0, None

    if line:
        rows.append(Row(line, device))

    return rows



def test_00():
    "find_break"    
    box = TextBox("123 567 90")
    assert find_goodbreak(box, 0) == None # not possible
    assert find_goodbreak(box, 1) == None # not possible
    assert find_goodbreak(box, 2) == None # not possible
    assert find_goodbreak(box, 3) == 4 # note that the space is not counted!
    assert find_goodbreak(box, 4) == 4
    assert find_goodbreak(box, 5) == 4
    assert find_goodbreak(box, 6) == 4
    assert find_goodbreak(box, 7) == 8
    assert find_goodbreak(box, 8) == 8
    assert find_goodbreak(box, 9) == 8
    assert find_goodbreak(box, 10) == 10 # no split necessary
    assert find_goodbreak(box, 11) == 10 # no split necessary


def test_01():
    boxes = []
    for text in "aa bb cc dd ee".split():
        boxes.append(TextBox(text))
        if text == 'dd':
            boxes.append(NewlineBox())

    assert str(simple_linewrap(boxes, 5)) == \
        "[Row[TB('aa'), TB('bb'), TB('c')], Row[TB('c'), TB('dd'), NL, "\
        "TB('ee')]]"

    boxes = []
    for text in "ff gg_hh ii jj".split('_'):
        boxes.append(TextBox(text))
    assert str(simple_linewrap(boxes, 5)) == \
        "[Row[TB('ff ')], Row[TB('gg'), TB('hh ')], Row[TB('ii jj')]]"
