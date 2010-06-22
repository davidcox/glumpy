#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
import string
import pyglet
from raw import *

def _make_pyglet_map():
    ret = {}
    for c in string.letters:
        ret[getattr(pyglet.window.key, c.upper())] = ord(c)
    for c in string.digits:
        ret[getattr(pyglet.window.key, "_"+c)] = ord(c)
    ret.update({
            pyglet.window.key.SPACE:     ord(' '),
            pyglet.window.key.BACKSPACE: ord('\b'),
            pyglet.window.key.RETURN:    ord('\r'),
            pyglet.window.key.PERIOD:    ord('.'),
            pyglet.window.key.MINUS:     ord('-'),
    })
    return ret

_pyglet_key_map = _make_pyglet_map()

_pyglet_button_map = {
    pyglet.window.mouse.LEFT:   TW_MOUSE_LEFT,
    pyglet.window.mouse.MIDDLE: TW_MOUSE_MIDDLE,
    pyglet.window.mouse.RIGHT:  TW_MOUSE_RIGHT,
}

def map_key(key):
    return _pyglet_key_map[key]

def map_button(button):
    return _pyglet_button_map[button]

def map_modifiers(modifiers):
    ret = TW_KMOD_NONE
    if modifiers & pyglet.window.key.MOD_SHIFT:
        ret |= TW_KMOD_SHIFT
    if modifiers & pyglet.window.key.MOD_CTRL:
        ret |= TW_KMOD_CTRL
    if modifiers & pyglet.window.key.MOD_ALT:
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
        if not button in _pyglet_button_map.keys():
            return False
        if TwMouseButton(TW_MOUSE_PRESSED, map_button(button)):
            self.window.draw()
            return True

    def on_mouse_release(self, x, y, button):
        if not button in _pyglet_button_map.keys():
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
