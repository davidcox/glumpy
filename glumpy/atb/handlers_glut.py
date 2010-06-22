#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import string
import glumpy
from raw import *

def _make_glumpy_map():
    ret = {}
    for c in string.letters:
        ret[getattr(glumpy.key, c.upper())] = ord(c)
    for c in string.digits:
        ret[getattr(glumpy.key, "_"+c)] = ord(c)
    ret.update({
            glumpy.key.SPACE:     ord(' '),
            glumpy.key.BACKSPACE: ord('\b'),
            glumpy.key.RETURN:    ord('\r'),
            glumpy.key.PERIOD:    ord('.'),
            glumpy.key.MINUS:     ord('-'),
    })
    return ret

_glumpy_key_map = _make_glumpy_map()

_glumpy_button_map = {
    glumpy.mouse.LEFT:   TW_MOUSE_LEFT,
    glumpy.mouse.MIDDLE: TW_MOUSE_MIDDLE,
    glumpy.mouse.RIGHT:  TW_MOUSE_RIGHT,
}

def map_key(key):
    return _glumpy_key_map[key]

def map_button(button):
    return _glumpy_button_map[button]

def map_modifiers(modifiers):
    ret = TW_KMOD_NONE
    if modifiers & glumpy.key.MOD_SHIFT:
        ret |= TW_KMOD_SHIFT
    if modifiers & glumpy.key.MOD_CTRL:
        ret |= TW_KMOD_CTRL
    if modifiers & glumpy.key.MOD_ALT:
        ret |= TW_KMOD_ALT
    return ret


class Handlers(object):

    def __init__(self, window):
        self.window = window

    def on_resize(self, width, height):
        TwWindowSize(width, height)

    def on_key_press(self, symbol, modifiers):
        try:
            TwKeyPressed(map_key(symbol), map_modifiers(modifiers))
            self.window.draw()
            return True
        except:
            pass 
        return False
    def on_mouse_press(self, x, y, button):
        if not button in _glumpy_button_map.keys():
            return False
        if TwMouseButton(TW_MOUSE_PRESSED, map_button(button)):
            self.window.draw()
            return True

    def on_mouse_release(self, x, y, button):
        if not button in _glumpy_button_map.keys():
            return False
        if TwMouseButton(TW_MOUSE_RELEASED, map_button(button)):
            self.window.draw()
            return True

    def on_mouse_drag(self, x, y, dx, dy, buttons):
        if TwMouseMotion(x, self.window.height-y):
            self.window.draw()
            return True

    def on_mouse_motion(self, x, y, dx, dy):
        if TwMouseMotion(x, self.window.height-y):
            self.window.draw()
            return True

    def on_draw(self):
        TwDraw()
