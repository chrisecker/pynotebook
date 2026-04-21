# -*- coding: utf-8 -*-

from .testdevice import TestDevice
from ..textmodel.viewbase import ViewBase, overridable_property
from ..textmodel.modelbase import Model
from ..textmodel.textmodel import dump_range
from ..textmodel.texeltree import length, iter_childs
from ..textmodel.utils import find_weight, get_weight, get_localroot, get_path
from ..textmodel import TextModel
from contextlib import contextmanager
import sys


debug = 0
#debug = 1

def undo(info):
    if callable(info[0]):
        func = info[0]
        args = info[1:]    
        redo = func(*args)
    else:
        redo = []
        for child in reversed(info):
            redo.append(undo(child))
    return redo


inf = sys.maxsize



def right_limit(texel, i0, i):
    if i <= i0 or i>= i0+length(texel):
        return inf 
    if texel.is_container: 
        mutability = texel.get_mutability()
        k = -1    
        for i1, i2, child in iter_childs(texel): 
            k += 1
            if i == i0+i1: 
                if not mutability[k]: 
                    return i
                return i0+i2 
            if i0+i1 < i < i0+i2:  # mitten in dem Element
                return min(i0+i2, right_limit(child, i0+i1, i))
    if texel.is_group:
        for i1, i2, child in iter_childs(texel): 
            if i0+i1 < i < i0+i2:  # mitten in dem Element
                return right_limit(child, i0+i1, i)
    return inf


def left_limit(texel, i0, i):
    # i ist im absoluten KS
    if i <= i0 or i>= i0+length(texel):
        return 0
    if texel.is_container: 
        mutability = texel.get_mutability()
        k = -1    
        for i1, i2, child in iter_childs(texel): 
            k += 1
            if i == i0+i2: 
                if not mutability[k]: 
                    return i
                return i0+i2 
            if i0+i1 < i < i0+i2:  # mitten in dem Element
                return max(i0+i1, left_limit(child, i0+i1, i))
    if texel.is_group:
        for i1, i2, child in iter_childs(texel):
            if i0+i1 < i < i0+i2:  # mitten in dem Element
                return left_limit(child, i0+i1, i)
    return 0


class TextView(ViewBase, Model):
    index = overridable_property('index')
    _index = 0
    selection = overridable_property('selection') # NOTE: i2 can also
                                                  # be smaller than
                                                  # i1!
    _selection = None
    layout = overridable_property('layout')
    maxw = overridable_property('maxw')
    _maxw = 0
    zoom = overridable_property('zoom')
    _zoom = 1.0
    _scrollrate = 10, 10
    _TextModel = TextModel
    editor = None

    highlights  = []
    squiggles   = []
    min_zoom    = 0.2
    max_zoom    = 5.0
    zoom_step   = 0.1

    _pending_range = None
    _inhibit_depth = 0

    def __init__(self):
        ViewBase.__init__(self)
        self.clear_undo()
        self.set_model(self._TextModel(''))
        assert self.builder is not None

    ### Editor slot

    editor_registry = []  # editor classes, priority order; subclasses may extend

    def try_install_click_editor(self):
        """Install a click_installable editor at the current index, if any matches.

        Returns True if an editor was installed.
        """
        path = get_path(self.model.get_xtexel(), self.index)
        for cls in self.editor_registry:
            if not cls.click_installable:
                continue
            m = cls.match(self, path)
            if m is not None:
                i1, i2, depth, texel = m
                editor = cls(self, i1, i2, depth)
                self.install_editor(editor, texel)
                return True
        return False

    def install_editor(self, editor, texel):
        editor.install(texel)
        self.editor = editor
        self.notify_views('editor_changed', editor)
        self.refresh()

    def reinstall_editor(self, texel):
        self.editor.reinstall(texel)

    def remove_editor(self):
        if self.editor is not None:
            self.editor = None
            self.notify_views('editor_changed', None)
            self.refresh()

    def update_editor(self):
        index = self.index
        editor = self.editor
        path = get_path(self.model.get_xtexel(), index)

        if editor is not None:
            m = editor.match(self, path)
            if m is not None:
                i1, i2, depth, texel = m
                assert i1 == editor.i1
                assert i2 == editor.i2
                self.reinstall_editor(texel)
                return
            self.remove_editor()

        for cls in self.editor_registry:
            if not cls.auto_installable:
                continue
            m = cls.match(self, path)
            if m is not None:
                i1, i2, depth, texel = m
                editor = cls(self, i1, i2, depth)
                self.install_editor(editor, texel)
                return

    def create_builder(self):
        # we install the BaseClass as a dummy builder
        from .builder import TestBuilder
        return TestBuilder()

    def clear_caches(self):
        self.builder.clear_caches()

    def set_model(self, model):
        ViewBase.set_model(self, model)
        self.builder = self.create_builder()
        self.rebuild()

    def get_layout(self):
        return self.builder.get_layout()
    
    def rebuild(self):
        self.builder.rebuild()
        self.refresh()

    def join_undo(self, info2, info1):
        # we are joining similar undo entries
        if 0:
            print("join")
            print("info1=", info1)
            print("info2=", info2)
        if info1[0] == info2[0]:
            if info1[0] == self._remove:
                i1, i2 = info1[1:]
                j1, j2 = info2[1:]
                if i2 == j1 and j2-i1<10:
                    return [(self._remove, i1, j2)]
            elif info1[0] == self._undo_remove:
                s, i1, i2 = info1[1:]
                t, j1, j2 = info2[1:]
                #print "i1, i2:", i1, i2
                #print "j1, j2:", j1, j2
                if j2 == i1 and i2-j1<10:
                    t.insert(len(t), s)
                    return [(self._undo_remove, t, j1, i2)]
                if i1 == j1 and i2-j1<10:
                    t.insert(0, s)
                    #print "remove:", repr(t.get_text()), i1, i2+j2-j1
                    return [(self._undo_remove, t, i1, i2+j2-j1)]
                    
        return [info2, info1]

    def undo(self):
        if len(self._undoinfo) > 0:
            self.add_redo(undo(self._undoinfo[0]))
            del self._undoinfo[0]
                
    def add_undo(self, info, clear_redo=1):
        if info is None:
            return
        if self._undo_group is not None:
            # Grouping active: collect instead of committing immediately.
            self._undo_group.append(info)
            return
        if len(self._undoinfo):
            joined = self.join_undo(info, self._undoinfo[0])
            self._undoinfo = joined + self._undoinfo[1:]
        else:
            self._undoinfo.insert(0, info)
        if clear_redo:
            self._redoinfo = []
        self.notify_views('undo_changed')

    def redo(self):
        if len(self._redoinfo) > 0:
            self.add_undo(undo(self._redoinfo[0]), 0)
            del self._redoinfo[0]

    def add_redo(self, info):
        # Internal method: add a single redo info
        self._redoinfo.insert(0, info)
        self.notify_views('undo_changed')

    def undocount(self):
        return len(self._undoinfo)

    def redocount(self):
        return len(self._redoinfo)

    def clear_undo(self):
        self._undoinfo = []
        self._redoinfo = []
        self._undo_group = None  # None = not grouping; list = collecting entries

    # ------------------------------------------------------------------
    # Undo grouping
    # ------------------------------------------------------------------

    def begin_undo_group(self):
        """Start collecting undo entries into a single group."""
        self._undo_group = []

    def end_undo_group(self):
        """Flush the collected group as one atomic undo entry."""
        group = self._undo_group
        self._undo_group = None
        if not group:
            return
        entry = group[0] if len(group) == 1 else group
        # Insert directly, bypassing join_undo (groups must not be merged).
        self._undoinfo.insert(0, entry)
        self._redoinfo = []
        self.notify_views('undo_changed')

    def insert(self, i, textmodel):
        self.model.insert(i, textmodel)
        self.index = i+len(textmodel)
        info = self._remove, i, i+len(textmodel)
        self.add_undo(info)

    def insert_text(self, i, text, **style):
        model = self.model.__class__(text, **style)  
        return self.insert(i, model)

    def remove(self, i1, i2):
        info = self._remove(i1, i2)
        self.add_undo(info)
        self.index = i1

    def _remove(self, i1, i2):
        old = self.model.remove(i1, i2)
        self.index = i1
        return self._undo_remove, old, i1, i2

    def _undo_remove(self, old, i1, i2):
        self.model.insert(i1, old)
        self.index = i2
        return self._remove, i1, i2

    def clear_styles(self, i1, i2):
        styles = self.model.clear_styles(i1, i2)
        info = self._set_styles, i1, styles
        self.add_undo(info)

    def set_properties(self, i1, i2, **properties):
        styles = self.model.set_properties(i1, i2, **properties)
        info = self._set_styles, i1, styles
        self.add_undo(info)

    def clear_properties(self, i1, i2, *keys):
        styles = self.model.clear_properties(i1, i2, *keys)
        info = self._set_styles, i1, styles
        self.add_undo(info)
        
    def _set_styles(self, i, styles):
        styles = self.model.set_styles(i, styles)
        return self._set_styles, i, styles

    def set_parstyle(self, i, style):
        styles = self.model.set_parstyle(i, style)
        info = self._set_parstyles, i, styles
        self.add_undo(info)

    def set_parproperties(self, i1, i2, **properties):
        styles = self.model.set_parproperties(i1, i2, **properties)
        info = self._set_parstyles, i1, styles
        self.add_undo(info)

    def clear_parproperties(self, i1, i2, *keys):
        styles = self.model.clear_parproperties(i1, i2, *keys)
        info = self._set_parstyles, i1, styles
        self.add_undo(info)
        
    def _set_parstyles(self, i, styles):
        styles = self.model.set_parstyles(i, styles)
        return self._set_parstyles, i, styles
    
    def transform(self, fun):
        # Apply a tranforming function to the texeltree. Can change
        # index.
        texel = self.model.texel
        new = fun(texel)
        info = self._set_texel(new)
        self.add_undo(info)

    def _set_texel(self, new):
        old = self.model.texel
        self.model.texel = new
        self.index = min(len(self.model), self.index)        
        self.rebuild()
        return self._set_texel, old

    def get_zoom(self):
        return self._zoom

    def set_zoom(self, zoom):
        self._zoom = zoom

    def get_maxw(self):
        return self._maxw

    def get_client_size(self):
        return 800, 600  # headless / test default; wx subclasses override

    def set_maxw(self, maxw):
        if maxw == self._maxw:
            return
        self._maxw = maxw
        self.builder.set_maxw(maxw)
        self.refresh()
        self.notify_views('maxw_changed')

    def insert_newline(self, index, style, parstyle):
        tmp = self._TextModel('\n', **style)
        tmp.set_parstyle(0, parstyle)
        self.insert(index, tmp)

    def compute_index(self, x, y):
        if y >= self.layout.height:
            return len(self.model)-1
        if y < 0:
            return 0
        return self.layout.get_index(x, y)

    _current_style = None

    def get_current_style(self):
        if self._current_style is None:
            index = self.index
            if index == 0:
                self._current_style = dict(self.model.get_style(index))
            else:
                self._current_style = dict(self.model.get_style(index - 1))
        return self._current_style

    def set_current_style(self, **properties):
        style = self.get_current_style()
        style.update(properties)
        self.notify_views('current_style_changed')

    def clear_current_style(self, *keys):
        style = self.get_current_style()
        for key in keys:
            style.pop(key, None)
        self.notify_views('current_style_changed')

    def handle_action(self, action, shift=False):
        model = self.model
        index = self.index
        layout = self.layout
        style = self.get_current_style()
        parstyle = model.get_parstyle(index)
        row, col = self.current_position()
        rect = layout.get_rect(index, 0, 0)
        x = rect.x1
        y = rect.y1
        if self.has_selection():
            s1, s2 = sorted(self.selection)
            e1, e2 = self.model.expand_range(s1, s2)
        else:
            s1 = s2 = e1 = e2 = index

        def del_selection():
            if self.has_selection():
                self.remove(e1, e2)

        if action == 'dump_info':
            dump_range(model.texel, e1, e2)
            row, col, i0 = model.index2position(index)
            print("index=", index)
            print("row=", row)
            print("col=", col)
            print("i0=", i0)

        elif action == 'dump_boxes':
            layout.dump_boxes(0, 0, 0)
        elif action == 'move_word_end':
            i = index
            n = len(model)
            try:
                while not model.get_text(i, i+1).isalnum():
                    i = i+1
                while model.get_text(i, i+1).isalnum():
                    i = i+1
            except IndexError:
                i = n
            self.set_index(i, shift)
        elif action == 'move_right':
            self.set_index(index+1, shift)
        elif action == 'move_word_begin':
            i = index
            try:
                while not model.get_text(i-1, i).isalnum():
                    i = i-1
                while model.get_text(i-1, i).isalnum():
                    i = i-1
            except IndexError:
                i = 0
            self.set_index(i, shift)
        elif action == 'move_left':
            self.set_index(index-1, shift)
        elif action == 'move_paragraph_end':
            i = model.linestart(index)
            n = len(model)
            while model.lineend(i) < n and model.linelength(i) == 1:
                i = model.lineend(i) + 1
            while model.lineend(i) < n and model.linelength(i) > 1:
                i = model.lineend(i) + 1
            self.set_index(i, shift)
        elif action == 'move_down':
            self.move_cursor_to(row+1, col, shift)
        elif action == 'move_paragraph_begin':
            i = model.linestart(index)
            while i > 0 and model.linelength(model.linestart(i - 1)) == 1:
                i = model.linestart(i - 1)
            while i > 0 and model.linelength(model.linestart(i - 1)) > 1:
                i = model.linestart(i - 1)
            self.set_index(i, shift)
        elif action == 'move_up':
            self.move_cursor_to(row-1, col, shift)
        elif action == 'move_line_start':
            self.set_index(model.linestart(index), shift)
        elif action == 'move_line_end':
            self.set_index(model.lineend(index), shift)
        elif action == 'move_page_down':
            _, height = self.get_client_size()
            i = self.compute_index(x, y + height / self.zoom)
            self.set_index(i, shift)
        elif action == 'move_page_up':
            _, height = self.get_client_size()
            i = self.compute_index(x, y - height / self.zoom)
            self.set_index(i, shift)
        elif action == 'move_document_start':
            self.set_index(0, shift)
        elif action == 'move_document_end':
            self.set_index(len(model), shift)
        elif action == 'select_all':
            self.selection = (0, len(model))
        elif action == 'insert_newline':
            self.insert_newline(index, style, parstyle)
        elif action == 'backspace':
            if self.has_selection():
                j1, j2 = self.model.expand_range(s1-1, s2)
                if j2 != e2:
                    self.remove(e1, e2)
                else:
                    self.remove(j1, j2)
            else:
                i = self.index
                if i>0:
                    j1, j2 = self.model.expand_range(i-1, i)
                    self.remove(j1, j2)
        elif action == 'copy':
            self.editor.copy() if self.editor is not None else self.copy()
        elif action == 'paste':
            self.editor.paste() if self.editor is not None else self.paste()
        elif action == 'cut':
            self.editor.cut() if self.editor is not None else self.cut()
        elif action == 'delete':
            if self.has_selection():
                del_selection()
            else:
                i = self.index
                if i < len(self.model):
                    j1, j2 = self.model.expand_range(i, i+1)
                    self.remove(j1, j2)
        elif action == 'undo':
            self.undo()
        elif action == 'redo':
            self.redo()
        elif action == 'del_line_end':
            el, off = get_localroot(model.texel, index)
            try:
                i = find_weight(el, row + 1, 2) - 1 + off
            except Exception:
                i = length(el) - 1 + off
            if i == index:
                i += 1
            i = min(i, right_limit(model.texel, 0, index))
            j1, j2 = self.model.expand_range(index, i)
            self.to_clipboard(model[j1:j2])
            self.remove(j1, j2)
        elif action == 'del_word_left':
            # find the beginning of the word
            i = index
            try:
                while not model.get_text(i-1, i).isalnum():
                    i = i-1
                while model.get_text(i-1, i).isalnum():
                    i = i-1
            except IndexError:
                i = 0
            i = max(i, left_limit(model.texel, 0, index))                
            j1, j2 = self.model.expand_range(i, index)
            self.remove(j1, j2)
        else:
            print("action: ", repr(action))
            assert len(action) == 1 # single character
            del_selection()
            self.insert_text(self.index, action, **style)
        self.refresh()

    def copy(self):
        if not self.has_selection():
            return        
        s1, s2 = self.get_selected()[0] # XXX Assuming just one region
        part = self.model[s1:s2]
        self.to_clipboard(part)

    def paste(self):
        if self.has_selection():
            for s1, s2 in self.get_selected():
                self.model.remove(s1, s2)
                self.index = s1
        textmodel = self.read_clipboard()
        if textmodel is not None:
            self.insert(self.index, textmodel)
                

    def cut(self):
        if self.has_selection():
            self.copy()
            for s1, s2 in self.get_selected():
                self.remove(s1, s2)
         
    def to_clipboard(self, textmodel):
        raise NotImplemented()

    def read_clipboard(self):
        raise NotImplemented()
         
    def select_word(self, x, y):
        i = self.layout.get_index(x, y)
        if i is None:
            return
        model = self.model
        n = len(model)
        try:
            while not model.get_text(i-1, i).isalnum():
                i = i-1
            while model.get_text(i-1, i).isalnum():
                i = i-1
        except IndexError:
            i = 0
        i1 = i
        i = i1
        try:
            while not model.get_text(i, i+1).isalnum():
                i = i+1
            while model.get_text(i, i+1).isalnum():
                i = i+1
        except IndexError:
            i = n
        i2 = i
        self.index = i2
        self.selection = (i1, i2)

    def refresh(self):
        pass

    def check(self):
        from ..textmodel.treebase import is_root_efficient
        assert is_root_efficient(self.layout)

    def rebuild_range(self, i1, i2, delta):
        self.builder.rebuild_range(i1, i2, delta)

    def _rebuild_with_progress(self, i1, i2, delta):
        self.builder.rebuild_range(i1, i2, delta)
        self.refresh()

    def ensure_viewport(self):
        pass

    def adjust_viewport(self):
        pass

    def ensure_index(self, index=None):
        pass

    def _accumulate(self, i1, i2, delta=0):
        self._pending_range = accumulate(self._pending_range, (i1, i2, delta))

    @contextmanager
    def atomic(self):
        """Group multiple model/stylesheet changes into one layout rebuild."""
        self.begin_undo_group()
        self._inhibit_depth += 1
        try:
            yield
        finally:
            self.end_undo_group()
            self._inhibit_depth -= 1
        if self._inhibit_depth == 0 and self._pending_range is not None:
            i1, i2, delta = self._pending_range
            self._pending_range = None
            self._rebuild_with_progress(i1, i2, delta)

    ### Signals issued by model
    def properties_changed(self, model, i1, i2):
        self.rebuild_range(i1, i2, 0)
        self.refresh()

    def inserted(self, model, i, n):
        if self.editor is not None:
            self.remove_editor()
        self.rebuild_range(i, i, n)
        if debug:
            self.check()
        if i>= self.index:
            self.index += n
        if self._selection is not None:
            s1, s2 = self.selection
            if i >= s1:
                s1 += n
            if i >= s2:
                s2 += n
            self.selection = s1, s2
        self.refresh()

    def removed(self, model, i, text):
        if self.editor is not None:
            self.remove_editor()
        self.rebuild_range(i, i, -len(text))
        n = len(text)
        i1 = i
        i2 = i+n
        m = len(model)
        index = self.index
        if index >= i2:
            self.index = index-n
        elif index > i1:
            self.index = i1
        if self._selection is not None:
            s1, s2 = self.selection
            if s1 >= i2:
                s1 -= n
            elif s1 > i1:
                s1 = i1
            if s2 >= i2:
                s2 -= n
            elif s2 > i1:
                s2 = i1
            self.selection = min(s1, m), min(s2, m)
        self.refresh()

    def keep_cursor_on_screen(self):
        pass
        
    ### Index
    def set_index(self, index, extend=False, update=True):
        old = self._index
        if index < 0:
            index = 0
        elif index > len(self.model):
            index = len(self.model)
        if index != self._index:
            self._index = index
            if index == 0:
                self._current_style = dict(self.model.get_style(0))
            else:
                self._current_style = dict(self.model.get_style(index - 1))
            if extend:
                self.extend_selection()
            elif update:
                self.start_selection()
            self.adjust_viewport()
            self.refresh()
            self.notify_views('index_changed')
        if old != index and self.editor is not None:
            self.remove_editor()
        self.update_editor()

    def get_index(self):
        return self._index

    def current_position(self):
        model = self.model
        i = self.index
        if model is None or i == 0:
            return 0, 0
        el, off = get_localroot(model.texel, i)
        local_i = i - off
        row = get_weight(el, 2, local_i)
        col = local_i - find_weight(el, row, 2)
        return row, col

    def move_cursor_to(self, row, col, extend=False, update=True):
        model = self.model
        el, off = get_localroot(model.texel, self.index)
        nlines = el.weights[2] + 1
        row = max(0, min(row, nlines - 1))
        ls = find_weight(el, row, 2)
        try:
            ll = find_weight(el, row + 1, 2) - ls
        except Exception:
            ll = length(el) - ls
        col = max(0, min(col, ll - 1))
        self.set_index(off + ls + col, extend, update)

    def get_selection(self):
        return self._selection

    def set_selection(self, selection):
        old = self._selection
        if selection == old:
            return
        if old is not None:
            i1, i2 = old
        self._selection = selection
        self.refresh()
        self.notify_views('selection_changed')

    def has_selection(self):
        selection = self.selection
        if selection is None:
            return False
        return selection[0] != selection[1]

    def get_selected(self):
        selection = self.selection
        if selection is None:
            return []
        s1, s2 = sorted(selection)
        if s1 == s2:
            return []
        if self.editor is not None:
            result = self.editor.selected(s1, s2)
            if result is not None:
                return result
        return [self.model.expand_range(s1, s2)]

    def start_selection(self):
        index = self.index
        self.selection = index, index
        
    def extend_selection(self):
        # Moves the selection endoint to index
        selection = self.selection
        index = self.index
        if selection is None:
            self.selection = index, index
        else:
            self.selection = selection[0], index


def accumulate(r1, r2):
    """Combine two consecutive update ranges into one.

    r1 = (i1, i2, delta) in original model coordinates.
    r2 = (b1, b2, d2)    in model coordinates after r1 was applied.
    """
    if r1 is None:
        return r2
    elif r2 is None:
        return r1

    pi1, pi2, pd = r1
    b1,  b2,  d2 = r2

    pi2_m0  = pi2 + max(0, -pd)
    pi1_m1  = pi1 + max(0,  pd)

    if b1 > pi1_m1:
        b1o = b1 - pd
        b2o = b2 - pd
    elif b2 < pi1:
        b1o = b1
        b2o = b2
    else:
        b1o = min(b1, pi1)
        b2o = max(b2 - pd, pi2_m0)

    return (min(pi1, b1o), max(pi2_m0, b2o), pd + d2)




class TestTextView(TextView):

    def create_builder(self):
        from .simplelayout import Builder
        return Builder(
            self.model,
            device=TestDevice(),
            maxw=80)

    
testtext = u"""Ein m\xe4nnlicher Briefmark erlebte
Was Sch\xf6nes, bevor er klebte.
Er war von einer Prinzessin beleckt.
Da war die Liebe in ihm geweckt.
Er wollte sie wiederk\xfcssen,
Da hat er verreisen m\xfcssen.
So liebte er sie vergebens.
Das ist die Tragik des Lebens.

(Joachim Ringelnatz)"""


def init_testing():
    model = TextModel(testtext)
    model.set_properties(15, 24, fontsize=14)
    model.set_properties(249, 269, fontsize=14)
    view = TestTextView()
    view.model = model
    assert len(view.layout) == len(model)+1
    return locals()


def test_00():
    "accumulate"
    assert accumulate((2, 5, 0), (8, 12, 0)) == (2, 12, 0)
    assert accumulate((8, 12, 0), (2, 5, 0)) == (2, 12, 0)
    assert accumulate((2, 8, 0), (5, 12, 0)) == (2, 12, 0)
    assert accumulate((5, 5, 1), (10, 10, 1)) == (5, 9, 2)
    assert accumulate((10, 10, 1), (3, 3, 1)) == (3, 10, 2)
    assert accumulate((5, 5, 3), (6, 6, 0)) == (5, 5, 3)
    assert accumulate((5, 5, -3), (7, 7, 0)) == (5, 10, -3)
    assert accumulate((5, 5, -3), (2, 3, 0)) == (2, 8, -3)
    assert accumulate((3, 3, 2), (8, 8, -4)) == (3, 6, -2)
    assert accumulate((5, 5, 2), (3, 10, 0)) == (3, 8, 2)
    assert accumulate((5, 5, -3), (3, 7, 0)) == (3, 10, -3)


def test_02():
    ns = init_testing()
    view = ns['view']
    view.cursor = 5
    view.selection = 3, 6
    return ns


def test_03():
    "set_properties, insert_text, remove"
    ns = init_testing()
    model = ns['model']
    model.set_properties(10, 20, fontsize=15)
    n = len(model)
    text = '\n12345\n'
    model.insert_text(5, text)
    model.remove(5, 5 + len(text))
    assert len(model) == n


def test_04():
    "insert/remove"
    ns = init_testing()
    model = ns['model']
    text = model.get_text()
    n = len(model)
    for i in range(len(text)):
        model.insert_text(i, 'X')
        assert len(model) == n + 1
        model.remove(i, i + 1)
        assert len(model) == n

    for i in range(n - 1):
        old = model.remove(i, i + 1)
        assert len(model) == n - 1
        model.insert(i, old)
        assert len(model) == n


def test_05():
    "join_undo"
    ns = init_testing()
    view = ns['view']
    for i, ch in enumerate('abcd'):
        view.add_undo(view.insert(i, TextModel(ch)))
    assert len(view._undoinfo) == 1

    view._undoinfo = []
    view.add_undo(view.remove(10, 11))
    view.add_undo(view.remove(9, 10))
    assert len(view._undoinfo) == 1
