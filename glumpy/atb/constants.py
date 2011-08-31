#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
''' AntTweakBar constants '''

# typedef enum ETwGraphAPI
(TW_OPENGL,
 TW_DIRECT3D9,
 TW_DIRECT3D10) = range(1,4)

# typedef enum ETwMouseButtonID
(TW_MOUSE_LEFT,
 TW_MOUSE_MIDDLE,
 TW_MOUSE_RIGHT) = range(1,4)

# typedef enum ETwMouseAction
(TW_MOUSE_RELEASED,
 TW_MOUSE_PRESSED) = range(0,2)

# typedef enum ETwType
(TW_TYPE_UNDEF,   TW_TYPE_BOOLCPP,  TW_TYPE_BOOL8,   TW_TYPE_BOOL16,
 TW_TYPE_BOOL32,  TW_TYPE_CHAR,     TW_TYPE_INT8,    TW_TYPE_UINT8, 
 TW_TYPE_INT16,   TW_TYPE_UINT16,   TW_TYPE_INT32,   TW_TYPE_UINT32,
 TW_TYPE_FLOAT,   TW_TYPE_DOUBLE,   TW_TYPE_COLOR32, TW_TYPE_COLOR3F,
 TW_TYPE_COLOR4F, TW_TYPE_CDSTRING, _,               TW_TYPE_QUAT4F,
 TW_TYPE_QUAT4D,  TW_TYPE_DIR3F,    TW_TYPE_DIR3D) = range(0,23)

# typedef enum ETwParamValueType
(TW_PARAM_INT32,
 TW_PARAM_FLOAT,
 TW_PARAM_DOUBLE,
 TW_PARAM_CSTRING) = range(0,4)

# typedef enum ETwKeyModifier
TW_KMOD_NONE  = 0x0000  
TW_KMOD_SHIFT = 0x0003
TW_KMOD_CTRL  = 0x00c0
TW_KMOD_ALT   = 0x0100
TW_KMOD_META  = 0x0c00


TW_KEY_BACKSPACE    = ord('\b')
TW_KEY_TAB          = ord('\t')
TW_KEY_CLEAR        = 0x0c
TW_KEY_RETURN       = ord('\r')
TW_KEY_PAUSE        = 0x13
TW_KEY_ESCAPE       = 0x1b
TW_KEY_SPACE        = ord(' ')
TW_KEY_DELETE       = 0x7f

(TW_KEY_UP,    
 TW_KEY_DOWN,
 TW_KEY_RIGHT,
 TW_KEY_LEFT,
 TW_KEY_INSERT,
 TW_KEY_HOME,
 TW_KEY_END,
 TW_KEY_PAGE_UP,
 TW_KEY_PAGE_DOWN,
 TW_KEY_F1,
 TW_KEY_F2,
 TW_KEY_F3,
 TW_KEY_F4,
 TW_KEY_F5,
 TW_KEY_F6,
 TW_KEY_F7,
 TW_KEY_F8,
 TW_KEY_F9,
 TW_KEY_F10,
 TW_KEY_F11,
 TW_KEY_F12,
 TW_KEY_F13,
 TW_KEY_F14,
 TW_KEY_F15,
 TW_KEY_LAST ) = range(273,273+25)
