# -*- coding: utf-8 -*-
"""Action handlers for different editing contexts.

Handlers have the signature:
    handler(view, action, shift, ctx) -> bool

Return True to stop the pipeline, False to pass to the next handler.
`ctx` is the SimpleNamespace built by TextView._build_ctx().
"""


def find_vertical(layout, index, x, dy):
    """Index on the nearest screen line above (dy=-1) or below (dy=1).

    Probes pixel by pixel because the area next to a line can still belong
    to the same cell (padding, gaps), where get_index maps back into it.
    """
    rect = layout.get_rect(index, 0, 0)
    y = rect.y1 - 1 if dy < 0 else rect.y2 + 1
    while 0 <= y <= layout.height:
        i = layout.get_index(x, y)
        if i is not None and layout.get_rect(i, 0, 0).y1 != rect.y1:
            return i
        y += dy


def text_handler(view, action, shift, ctx):
    """X-coordinate-based movement for wrapped (word-processor) text.

    Overrides move_up/move_down to track the visual x position across
    line breaks and cell boundaries rather than the character column.
    All other actions fall through to the next handler.
    """
    if action in ('move_up', 'move_down'):
        dy = -1 if action == 'move_up' else 1
        i = find_vertical(ctx.layout, ctx.index, ctx.x, dy)
        if i is not None:
            view.set_index(i, shift)
        return True
    return False


def code_handler(view, action, shift, ctx):
    """Row/column-based movement and space-indentation for code views.

    Overrides move_up/move_down (character-column based) and indent/dedent
    (leading-space insertion). All other actions fall through.
    """
    if action == 'move_up':
        view.move_cursor_to(ctx.row - 1, ctx.col, shift)
        return True
    elif action == 'move_down':
        view.move_cursor_to(ctx.row + 1, ctx.col, shift)
        return True
    elif action == 'indent':
        s1, s2 = ctx.s1, ctx.s2
        view.shift(s1, s2)
        return True
    elif action == 'dedent':
        s1, s2 = ctx.s1, ctx.s2
        view.unshift(s1, s2)
        return True
    return False
