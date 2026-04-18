# -*- coding: utf-8 -*-

# Noch nicht commitet

from copy import copy as shallow_copy


class EndReached(IndexError):
    pass

class BeginReached(IndexError):
    pass

class BoxIter:
    current = None
    i = None
    def __init__(self, tree, i):
        # NOTE:
        # - der Stack hat Einträge (node, index)        
        # - der Eintrag bedeutet dass das nächste Element (im Stack
        #   bzw. current) ein Kind von Node mit dem Index ist        
        # - (node, 2) kann gelesen werden als "drittes Kind von Node"        
        # - current ist also immer stack[-1][0].childs[stack[-1][1]]
        self.stack = []
        i1 = 0
        node = tree
        if i>=len(tree):
            raise Exception("Index %i liegt nicht in dem Tree." % i)
            
        while True:
            childs = [l[2] for l in node.iter_childs()]
            if (not childs) or self.stop_descend(node):
                self.i = i1
                self.current = node
                return
            
            for idx, child in enumerate(childs):                
                i2 = i1+len(child)
                if i2>i:
                    # Steige ab
                    self.stack.append((node, idx))
                    node = child
                    break
                i1 = i2

    def copy(self):
        return shallow_copy(self)

    def stop_descend(self, node):
        # Kann überschrieben werden, um nach bestimmten Noden zu
        # suchen, z.B. Noden einer bestimmten Klasse. Bei dem
        # Rückgabewert True wird der Abstieg beendet.
        return False
        
    def move_left(self):
        # Hochgehen bis linker Sibling existiert
        stack = self.stack[:]
        depth = len(stack)
        while stack:
            parent, idx = stack.pop()
            if idx > 0:
                # es existiert linker Sibling
                idx -= 1
                stack.append((parent, idx))
                break            
        else:
            raise BeginReached("Kein linker Node auf gleicher Tiefe")

        # Absteigen auf Zielhöhe
        parent, idx = stack[-1]
        current = parent.childs[idx]
        while len(stack) < depth:
            stack.append((current, len(current.childs)-1))
            current = current.childs[-1]
        self.current = current
        self.i -= len(self.current)
        self.stack = stack

    def move_right(self):
        # Hochgehen bis rechter Sibling existiert
        stack = self.stack[:]
        depth = len(stack)
        while stack:
            parent, idx = stack.pop()
            if len(parent.childs) > idx+1:
                # es existiert rechter Sibling
                idx += 1
                stack.append((parent, idx))
                break            
        else:
            raise EndReached("Kein rechter Node auf gleicher Tiefe")

        # Absteigen auf Zielhöhe, dabei immer links abbiegen
        parent, idx = stack[-1]
        current = parent.childs[idx]
        while len(stack) < depth:
            stack.append((current, 0))
            current = current.childs[0]
        self.i += len(self.current)
        self.current = current
        self.stack = stack

        
