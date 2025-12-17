# -*- coding: latin-1 -*-

from .testdevice import TESTDEVICE
from .boxes import TabulatorBox, TextBox, EmptyTextBox, NewlineBox, Row



def find_goodbreak(box, maxw):
    """Letztes Leerzeichen innerhalb maxw suchen."""
    if not isinstance(box, TextBox) or maxw <= 0:
        return None

    text = box.text
    parts = box.measure_parts(text)

    for i in range(len(text) - 1, -1, -1):
        if text[i] == ' ' and parts[i] <= maxw:
            return i + 1
    return None

def find_anybreak(box, maxw):
    """Ersten Überlauf finden."""
    if not isinstance(box, TextBox) or maxw <= 0:
        return 0

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


def simple_linewrap(boxes, maxw, wordwrap=True, device=TESTDEVICE):
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

        # Versuch innerhalb der Box zu brechen
        avail = maxw - w
        i = find_goodbreak(box, avail) if wordwrap else find_anybreak(box, avail)

        # Rückgriff auf letztes Leerzeichen der Zeile
        if i is None and last_space:
            k, j = last_space
            a, b = split_box(line[k], j)

            boxes = [b] + line[k + 1:] + [box] + boxes
            line = line[:k] + [a]
            rows.append(Row(line, device))

        else:
            if i is None:
                i = find_anybreak(box, avail)

            a, b = split_box(box, i)
            if i > 0:
                line.append(a)
            boxes = [b] + boxes if b else boxes
            rows.append(Row(line, device))

        # neue Zeile
        line, w, last_space = [], 0, None

    if line:
        rows.append(Row(line, device))

    return rows



def test_00():
    "find_break"
    box = TextBox("123 567 90")
    assert find_goodbreak(box, 3) == None
    assert find_goodbreak(box, 4) == 4
    assert find_goodbreak(box, 5) == 4
    assert find_goodbreak(box, 6) == 4
    assert find_goodbreak(box, 7) == 4
    assert find_goodbreak(box, 8) == 8
    assert find_goodbreak(box, 9) == 8
    assert find_goodbreak(box, 10) == 8
    assert find_goodbreak(box, 11) == 8 # XXX Hmm?


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
    print(str(simple_linewrap(boxes, 5)))
    assert str(simple_linewrap(boxes, 5)) == \
        "[Row[TB('ff ')], Row[TB('gg'), TB('hh ')], Row[TB('ii jj')]]"
