# -*- coding: utf-8 -*-
from .texeltree import NewLine, length, iter_childs, fuse, grouped, \
    provides_childs, Group


def iter_leafes(texel, i, descend_containers=False):
    """Iterates through all leaf-elements starting at i. """

    l = [[texel]]
    i1 = 0
    while 1:
        while l and not l[-1]:
            l.pop()
        if not l:
            break
        ll = l[-1]
        elem = ll[0]
        del ll[0]
        n = length(elem)
        if i1+n <= i:
            i1 = i1+n
        elif elem.is_group:
            l.append(list(elem.childs))
        elif elem.is_container and descend_containers:
            l.append(list(elem.childs))
        else:
            i2 = i1+n
            yield i1, i2, elem
            i1 = i2

def iter_newlines(texel, i, descend_containers=False):
    """Find all NewLine-Texels at or after position i.
    """
    for j1, j2, elem in iter_leafes(texel, i, descend_containers):
        if isinstance(elem, NewLine):
            yield j1, j2, elem


def iter_paragraphs(texel, i, descend_containers=False):
    """Break the texel material into paragraphs. Yields for each
    paragraph begin, end and list of texels.
    """
    l = []
    i1 = 0
    for j1, j2, elem in iter_leafes(texel, i, descend_containers):
        l.append(elem)
        if isinstance(elem, NewLine):
            yield i1, j2, l
            l = []
            i1 = j2


def get_newlines(texel, i1, i2, _offset=0):
    """Yield (abs_pos, nl) for all NewLines in [i1, i2).

    Descends into both Groups and Containers, so works inside table cells.
    """
    if texel.is_group or texel.is_container:
        for j1, j2, child in iter_childs(texel):
            if j2 <= i1 or j1 >= i2:
                continue
            yield from get_newlines(child, i1 - j1, i2 - j1, _offset + j1)
    elif isinstance(texel, NewLine):
        if i1 <= 0 < i2:
            yield _offset, texel


def transform_range(texel, i1, i2, fun):
    """Apply fun to all texels in [i1, i2), descending into containers.

    Returns a list of texels.  Groups and Containers are treated identically.
    """
    if texel.is_group or texel.is_container:
        r1 = []; r2 = []; r3 = []
        for j1, j2, child in iter_childs(texel):
            if j2 <= i1:
                r1.append(child)
            elif j1 >= i2:
                r3.append(child)
            else:
                r2 = fuse(r2, transform_range(child, i1 - j1, i2 - j1, fun))
        if texel.is_container:
            return [texel.set_childs(r1 + r2 + r3)]
        return fuse(r1, r2, r3)
    elif texel.is_single:
        if i1 >= 1 or i2 <= 0:
            return [texel]
        return [fun(texel)]
    elif texel.is_text:
        from .texeltree import T
        r = []
        text = texel.text
        n = len(text)
        i1 = max(0, i1)
        i2 = min(n, i2)
        if i1:
            r.append(T(text[:i1], texel.style))
        if i2 > i1:
            r.append(fun(T(text[i1:i2], texel.style)))
        if i2 < n:
            r.append(T(text[i2:], texel.style))
        return r
    return [texel]


def find_texel(tree, texel, i):
    """Search for texel by identity in tree at position i.

    Returns (i1, i2, depth): absolute interval and depth of the texel.
    """
    if tree is texel:
        return 0, length(tree), 0
    if not provides_childs(tree):
        raise IndexError("Texel not found at position %i" % i)
    for j1, j2, child in iter_childs(tree):
        if j1 <= i < j2:
            i1_rel, i2_rel, depth = find_texel(child, texel, i - j1)
            return i1_rel + j1, i2_rel + j1, depth + 1
    raise IndexError("Texel not found at position %i" % i)


def get_texel(tree, i, depth):
    """Return the texel at position i and the given depth."""
    if depth == 0:
        if 0 <= i < length(tree):
            return tree
        raise IndexError("Position %i out of bounds" % i)
    if not provides_childs(tree):
        raise IndexError("Depth %i not reachable at position %i" % (depth, i))
    for j1, j2, child in iter_childs(tree):
        if j1 <= i < j2:
            return get_texel(child, i - j1, depth - 1)
    raise IndexError("No child covers position %i at depth %i" % (i, depth))


def transform_node(tree, i, d, fun):
    """Apply fun to the single node at position i and depth d."""
    if d == 0:
        return fun(tree)
    if not provides_childs(tree):
        raise IndexError("Can't descend into texel %s" % repr(tree))
    r = []
    for j1, j2, child in iter_childs(tree):
        if j1 <= i < j2:
            r.append(transform_node(child, i - j1, d - 1, fun))
        else:
            r.append(child)
    if tree.is_group:
        return Group(r)
    assert tree.is_container
    return tree.set_childs(r)


def get_path(tree, i, _offset=0):
    """Return the path of nodes covering position i.

    Returns a list of (abs_i1, abs_i2, node) tuples from root to leaf.
    """
    path = [(_offset, _offset + length(tree), tree)]
    if provides_childs(tree):
        for j1, j2, child in iter_childs(tree):
            if j1 <= i < j2:
                return path + get_path(child, i - j1, _offset + j1)
    return path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_00():
    "iter_leafes"
    from .texeltree import T, G, Container
    t1 = T("012345678")
    t2 = T("ABC")
    t3 = T("xyz")
    c = Container().set_childs((t2, t3))
    g = G((t1, c))
    l = []
    for i1, i2, elem in iter_leafes(g, 0):
        l.append((i1, i2, elem))
    assert repr(l) == "[(0, 9, T('012345678')), (9, 15, C([T('ABC'), T('xyz')]))]"


def test_01():
    "get_newlines descends into containers"
    from .texeltree import G, NL, Container
    nl1 = NL.set_indent(1)
    nl2 = NL.set_indent(2)
    c = Container().set_childs([nl1])
    g = G([nl2, c])
    # nl2 at pos 0, c at pos 1..2 (nl1 inside)
    result = list(get_newlines(g, 0, 3))
    assert len(result) == 2
    assert result[0] == (0, nl2)
    assert result[1] == (1, nl1)


def test_02():
    "transform_range descends into containers"
    from .texeltree import G, NL, Container, length
    nl = NL.set_indent(0)
    c = Container().set_childs([nl])
    g = G([c])

    called = []
    def fun(texel):
        if isinstance(texel, NewLine):
            called.append(texel)
            return texel.set_indent(3)
        return texel

    result = transform_range(g, 0, length(g), fun)
    assert called, "fun was not called"
    result_g = G(result)
    inner_nl = result_g.childs[0].childs[0]
    assert inner_nl.indent == 3


def test_03():
    "expand_range: selection not touching any separator is unchanged"
    from .textmodel import TextModel
    from .texeltree import Fraction, Text
    m = TextModel()
    m.texel = Fraction(Text("a"), Text("b"))
    assert m.expand_range(1, 2) == (1, 2)


def test_04():
    "expand_range: selection spanning a separator expands to full container"
    from .textmodel import TextModel
    from .texeltree import Fraction, Text, length
    m = TextModel()
    m.texel = Fraction(Text("a"), Text("b"))
    assert m.expand_range(1, 4) == (0, length(m.texel))


def test_05():
    "expand_range: selection touching left separator expands to full container"
    from .textmodel import TextModel
    from .texeltree import Fraction, Text, length
    m = TextModel()
    m.texel = Fraction(Text("a"), Text("b"))
    assert m.expand_range(0, 1) == (0, length(m.texel))


def test_06():
    "get_path"
    from .texeltree import G, T, Fraction
    tree = G([Fraction(T('A'), T('B'))])
    path = get_path(tree, 1)
    assert len(path) == 3
    assert path[0] == (0, 5, tree)
    assert path[1][2].is_container
    assert path[2] == (1, 2, path[1][2].childs[1])


def test_07():
    "get_texel"
    from .texeltree import G, T, Fraction
    a = T('A')
    b = T('B')
    f = Fraction(a, b)
    assert get_texel(f, 0, 0) is f
    assert get_texel(f, 1, 1) is a
    assert get_texel(f, 3, 1) is b
    assert get_texel(f, 0, 1) is f.childs[0]
    assert get_texel(f, 2, 1) is f.childs[2]
    assert get_texel(f, 4, 1) is f.childs[4]


def test_08():
    "find_texel"
    from .texeltree import G, T, Fraction
    a = T('A')
    b = T('B')
    f = Fraction(a, b)
    assert find_texel(f, f, 0) == (0, 5, 0)
    tree = G([f, T('C')])
    assert find_texel(tree, f, 0) == (0, 5, 1)
    assert find_texel(tree, a, 1) == (1, 2, 2)
    try:
        find_texel(tree, a, 2)
        assert False
    except IndexError:
        pass


def test_09():
    "transform_node"
    from .texeltree import G, T, Fraction, get_text
    a = T('A')
    b = T('B')
    c = T('C')
    x = T('X')
    f = Fraction(a, b)
    replace = lambda old: x
    assert find_texel(f, a, 1) == (1, 2, 1)
    assert get_text(transform_node(f, 1, 1, replace)) == '\nX\nB\n'
    assert get_text(transform_node(f, 3, 1, replace)) == '\nA\nX\n'
    tree = G([f, c])
    assert get_text(transform_node(tree, 1, 2, replace)) == '\nX\nB\nC'
    try:
        transform_node(tree, 1, 3, replace)
        assert False
    except IndexError:
        pass
