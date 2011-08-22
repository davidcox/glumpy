#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# glumpy is an OpenGL framework for the fast visualization of numpy arrays.
# Copyright (C) 2009-2011  Nicolas P. Rougier. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY NICOLAS P. ROUGIER ''AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL NICOLAS P. ROUGIER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Nicolas P. Rougier.
# -----------------------------------------------------------------------------
'''
A Figure represents a rectangular area on a window that can be used to
display graphics and received events.
'''
import sys
import numpy as np
import OpenGL.GL as gl

from event import EventDispatcher, EVENT_HANDLED, EVENT_UNHANDLED
from window import Window, active_window
import key, mouse


# ------------------------------------------------------------------ figure ---
def figure(size = (800,600), position = (0,0)):
    ''' Helper function to create a figure '''

    fig = Figure(size=size, position=position, parent=None)
    return fig._figures[0]



# ------------------------------------------------------------------ show ---
def show():
    ''' Show all figures '''

    active_window().mainloop()




# --------------------------------------------------------- FigureException ---
class FigureException(Exception):
    '''The root exception for all figure-related errors.'''
    pass




# ------------------------------------------------------------------ Figure ---
class Figure(EventDispatcher):
    '''
    A Figure represents a rectangular area on a window that can be used to
    display graphics and received events.

    :Example:

    .. code-block:: python

       fig = Figure()

       @fig.event
       def on_draw():
           draw_something()

       fig.show()
    '''


    # ---------------------------------------------------------------- init ---
    def __init__(self, size = (800,600), position = (0,0), parent = None):
        '''
        :Parameters:
            ``size``: (int,int)
                Absolute size in pixels.

            ``position``:
                Absolute position in pixels.

            ``parent``: Figure or Window
                Parent Figure or Window
        '''

        EventDispatcher.__init__(self)
        self._size     = size
        self._position = position
        self._parent = parent
        self._figures  = []
        if parent is None:
            w,h = size[0], size[1]
            self._root = Window(width=int(w), height=int(h),
                                caption='Figure', visible=True)
            self._root.push_handlers(self)
            fig = Figure(size=(1.0,1.0), position=(0,0), parent = self)
            self._figures.append(fig)



    # -------------------------------------------------------------- parent ---
    def _get_parent(self):
        ''' Get parent figure. '''
        return self._parent
    parent = property(_get_parent,
         doc='''
         Parent figure. Read-only.
         
         :type: Figure
         ''')



    # ---------------------------------------------------------------- root ---
    def _get_root(self):
        ''' Get root window. '''
        parent = self
        while parent is not None:
            if parent.parent is None:
                return parent._root
            parent = parent.parent
    root = property(_get_root,
         doc='''
         Root window. Read-only.
         
         :type: Window
         ''')



    # --------------------------------------------------------------- width ---
    def _get_width(self):
        ''' Get figure width in pixels '''
        if self.parent is None:
            return self._size[0]
        else:
            return self._size[0]*self.parent.width
    width = property(_get_width,
         doc='''
         Figure width in pixels. Read-only.
         
         :type: int
         ''')


   
    # -------------------------------------------------------------- height ---
    def _get_height(self):
        if self.parent is None:
            return self._size[1]
        else:
            return self._size[1]*self.parent.height
    height = property(_get_height,
         doc='''
         Figure height in pixels. Read-only.
         
         :type: int
         ''')



    # ------------------------------------------------------------------- x ---
    def _get_x(self):
        ''' Get figure x coordinate relatively to parent figure origin'''
        if self.parent is None:
            return 0
        else:
            return self._position[0]*self.parent.width
    x = property(_get_x,
         doc='''
         Figure x coordinate relatively to parent figure origin. Read-only.
         
         :type: int
         ''')



    # ------------------------------------------------------------------- y ---
    def _get_y(self):
        ''' Get figure x coordinate relatively to parent figure origin'''
        if self.parent is None:
            return 0
        else:
            return self._position[1]*self.parent.height
    y = property(_get_y,
         doc='''
         Figure y coordinate relatively to parent figure origin. Read-only.
         
         :type: int
         ''')



    # ------------------------------------------------------------------- X ---
    def _get_X(self):
        ''' Get figure absolute x coordinate'''
        if self.parent is None:
            return 0
        else:
            return self.x + self.parent.X
    X = property(_get_X,
         doc='''
         Figure absolute x coordinate. Read-only.
         
         :type: int
         ''')



    # ------------------------------------------------------------------- Y ---
    def _get_Y(self):
        ''' Get figure absolute y coordinate'''
        if self.parent is None:
            return 0
        else:
            return self.y + self.parent.Y
    Y = property(_get_Y,
         doc='''
         Figure absolute y coordinate. Read-only.
         
         :type: int
         ''')



    # ------------------------------------------------------------ viewport ---
    def _get_viewport(self):
        ''' Get figure absolute viewport'''
        return (int(round(self.X)), int(round(self.Y)), 
                int(round(self.width)), int(round(self.height)))
    viewport = property(_get_viewport,
         doc='''
         Figure absolute viewport as (x,y,width,height). Read-only.
         
         :type: tuple of 4 int
         ''')



    # -------------------------------------------------------------- figure ---
    def add_figure(self, cols = 1, rows = 1, position = (0,0), size = (1,1)):
        '''
        Add a figure to the current figure.

        :Parameters:

            ``cols``: int
                
            ``row``: int

            ``position``: (int,int)

            ``size``: (int,int)

            
        '''

        hborder, vborder = 0, 0
        if type(cols) is int:
            cols = [1,]*cols
        elif type(cols) is float:
            cols = [1,]*int(cols) + [cols-int(cols),]
        p = np.array(cols).astype(float)
        hborder = np.resize(np.array(hborder),len(cols)*2)
        hsize = (p / p.sum()) * (1-hborder.sum())

        if type(rows) is int:
            rows = [1,]*int(rows)
        elif type(rows) is float:
            rows = [1,]*rows + [rows-int(rows),]
        p = np.array(rows).astype(float)
        vborder = np.resize(np.array(vborder),len(rows)*2)
        vsize = (p / p.sum()) * (1-vborder.sum())

        col, row = position
        width, height = size
        x0 = hsize[0:col       ].sum() + hborder[0:1+2*col           ].sum()
        x1 = hsize[0:col+width ].sum() + hborder[0:1+2*(col+width)-2 ].sum()
        y0 = vsize[0:row       ].sum() + vborder[0:1+2*row           ].sum()
        y1 = vsize[0:row+height].sum() + vborder[0:1+2*(row+height)-2].sum()

        fig = Figure(size=(x1-x0,y1-y0), position=(x0,y0), parent=self)
        self._figures.append(fig)
        return fig





    # --------------------------------------------------------------- split ---
    def split(self, position = 'right', size = 0.5):
        '''
        Split the figure into two figures.

        :Parameters:

            ``position``: 'left', 'right', 'top' or 'bottom'
                Position of the newly created figure.

            ``size``: float
                Relative size of the newly created figure.
        '''

        parent   = self._parent
        w,h = self._size
        x,y = self._position
        spacing = 0
        if position == 'right':
            w1, w2 = (1-size-spacing/2.0)*w,  (size-spacing/2.0)*w
            h1, h2 = h, h
            x1, x2 = x, x+w1+spacing
            y1, y2 = y, y
        elif position == 'left':
            w1, w2 = (1-size-spacing/2.0)*w,  (size-spacing/2.0)*w
            h1, h2 = h, h
            x1, x2 = x+w2+spacing, x
            y1, y2 = y, y
        elif position == 'top':
            w1, w2 = w, w
            h1, h2 = (1-size-spacing/2.0)*h,  (size-spacing/2.0)*h
            x1, x2 = x, x
            y1, y2 = y, y+h1+spacing
        elif position == 'bottom':
            w1, w2 = w, w
            h1, h2 = (1-size-spacing/2.0)*h,  (size-spacing/2.0)*h
            x1, x2 = x, x
            y1, y2 = y+h2+spacing, y
        self._size     = w1,h1
        self._position = x1,y1

        fig = Figure(size=(w2,h2), position=(x2,y2), parent=parent)
        parent._figures.append(fig)
        return fig


    # -------------------------------------------------------------- add_frame ---
    def add_frame(self, size = (0.9,0.9), aspect=None):
        ''' '''
        frame = Frame(self, size=size, aspect=aspect)
        self.parent._figures.append(frame)
        self._aspect = aspect
        return frame



    # --------------------------------------------------------------- clear ---
    def clear(self, red=1, green=1, blue=1, alpha=1):
        '''
        Clear the current figure with given color.

        :Parameter:

            ``red``: float
                Red component

            ``green``: float
                Green component

            ``blue``: float
                Blue component

            ``alpha``: float
                Alpha component (transparency)
        '''
        gl.glClearColor(red,green,blue,alpha)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)



    # ---------------------------------------------------------------- show ---
    def show(self):
        '''
        Show all figures and enter the mainloop.
        '''

        if self.parent is not None:
            self.parent.show()
            return
        self._root.mainloop()


    # ---------------------------------------------------------------- show ---
    def draw(self):
        '''
        Show all figures and enter the mainloop.
        '''

        self.root.draw()


    # ---------------------------------------------------------------- push ---
    def push(self, obj):
        '''
        Push object handlers onto the event stack

        :Parameters:

            ``obj``: object
                Object to be pushed onto the event stack

        '''

        self.push_handlers(obj)

    # ---------------------------------------------------------------- push ---
    def pop(self, obj=None):
        '''
        Pop given object from the event stack. If obj is None, the last objects
        is removed.

        :Parameters:

            ``obj``: object or None
                Object to be removed out from the event stack
        '''

        if obj is None:
            self.pop_handlers(obj)
        else:
            self.remove_handlers(obj)




    # -------------------------------------------------------- __contains__ ---
    def __contains__(self, point):
        '''
        Return true if point is contained in figure viewport
        '''

        x,y,w,h = self.viewport
        return x <= point[0] <= x+w and y <= point[1] <= y+h



    # ------------------------------------------------------------- on_init ---
    def on_init(self):
        '''
        OpenGL setup.
        
        The event loop will dispatch this event to all subfigures before
        entering mainloop and the figure will already have a valid GL context.
        '''

        gl.glEnable (gl.GL_DEPTH_TEST)
        gl.glEnable (gl.GL_LIGHT0)
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_DIFFUSE,  (1.0, 1.0, 1.0, 1.0))
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_AMBIENT,  (0.1, 0.1, 0.1, 1.0))
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
        gl.glLightfv (gl.GL_LIGHT0, gl.GL_POSITION, (0.0, 1.0, 2.0, 1.0))
        gl.glEnable (gl.GL_BLEND)
        gl.glEnable (gl.GL_COLOR_MATERIAL)
        gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        
        for fig in self._figures:
            invoked = fig.dispatch_event('on_init')
            if invoked == EVENT_HANDLED: return invoked

        return EVENT_UNHANDLED



    # ---------------------------------------------------------------- timer ---
    def timer(self, *args):
        '''
        Function decorator for a timed handler.
        '''
        return self.root.timer(*args)



    # ------------------------------------------------------------- on_draw ---
    def on_draw(self):
        '''
        The window contents must be redrawn.

        The event loop will dispatch this event to all subfigures.  This will
        happen during idle time after any figure events and after any scheduled
        functions were called.

        You should make no assumptions about the window contents when this
        event is triggered; a resize or expose event may have invalidated the
        framebuffer since the last time it was drawn.
        '''

        for fig in self._figures:
            x,y,w,h = fig.viewport
            gl.glPushAttrib(gl.GL_VIEWPORT_BIT | gl.GL_SCISSOR_BIT)
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glPushMatrix()
            gl.glLoadIdentity()
            gl.glViewport(x,y,w,h)
            gl.glEnable(gl.GL_SCISSOR_TEST)
            gl.glScissor(x,y,w,h)
            gl.glOrtho(0, w, 0, h, -1000, 1000)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            fig.dispatch_event('on_draw')
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glPopMatrix()
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPopAttrib()



    # ----------------------------------------------------------- on_resize ---
    def on_resize(self, width, height):
        '''
        A resize event occured.

        :Parameters:

            ``width`` : int
                New figure width

            ``height`` : int
                New figure height
        '''

        if self._parent is None:
            self._size = width, height
            
        for fig in self._figures:
            invoked = fig.dispatch_event('on_resize', fig.width, fig.height)
            if invoked == EVENT_HANDLED: return invoked

        return EVENT_UNHANDLED


        
    # -------------------------------------------------------- on_key_press ---
    def on_key_press(self, symbol, modifiers):
        '''
        A key on the keyboard was pressed.

        :Parameters:

            ``symbol`` : int
                The key symbol pressed.

            ``modifiers`` : int
                Bitwise combination of the key modifiers active.
        '''

        for fig in self._figures:
            invoked = fig.dispatch_event('on_key_press', symbol, modifiers)
            if invoked == EVENT_HANDLED: return invoked
        return EVENT_UNHANDLED



    # -------------------------------------------------------- on_key_press ---
    def on_key_release(self, symbol, modifiers):
        '''
        A key on the keyboard was released.

        :Parameters:
            symbol : int
                The key symbol pressed.
            modifiers : int
                Bitwise combination of the key modifiers active.
        '''

        for fig in self._figures:
            invoked = fig.dispatch_event('on_key_release', symbol, modifiers)
            if invoked == EVENT_HANDLED: return invoked
        return EVENT_UNHANDLED



    # ------------------------------------------------------ on_mouse_press ---
    def on_mouse_press(self, x, y, button):
        '''
        A mouse button was pressed.

        :Parameters:
            ``x`` : int
                Distance in pixels from the left edge of the figure.
            ``y`` : int
                Distance in pixels from the bottom edge of the figure.
            ``button`` : int
                The mouse button that was released.
        '''

        for fig in self._figures:
            if (x,y) in fig:
                invoked = fig.dispatch_event('on_mouse_press',
                                            x-fig.X, y-fig.Y, button)
                if invoked == EVENT_HANDLED: return invoked
        return EVENT_UNHANDLED



    # ---------------------------------------------------- on_mouse_release ---
    def on_mouse_release(self, x, y, button):
        '''
        A mouse button was released.

        :Parameters:
            ``x`` : int
                Distance in pixels from the left edge of the figure.
            ``y`` : int
                Distance in pixels from the bottom edge of the figure.
            ``button`` : int
                The mouse button that was released.
        '''

        for fig in self._figures:
            if (x,y) in fig:
                invoked = fig.dispatch_event('on_mouse_release',
                                            x-fig.X, y-fig.Y, button)
                if invoked == EVENT_HANDLED: return invoked
        return EVENT_UNHANDLED


    # ----------------------------------------------------- on_mouse_motion ---
    def on_mouse_motion(self, x, y, dx, dy):
        '''
        The mouse was moved with no buttons held down.

        :Parameters:

            ``x`` : int
                Distance in pixels from the left edge of the figure.

            ``y`` : int
                Distance in pixels from the bottom edge of the figure.

            ``dx`` : int
                Relative X position from the previous mouse position.

            ``dy`` : int
                Relative Y position from the previous mouse position.
        '''


        for fig in self._figures:
            if (x,y) in fig:
                invoked = fig.dispatch_event('on_mouse_motion',
                                            x-fig.X, y-fig.Y, dx,dy)
                if invoked == EVENT_HANDLED: return invoked
        return EVENT_UNHANDLED


    # ------------------------------------------------------- on_mouse_drag ---
    def on_mouse_drag(self, x, y, dx, dy, button):
        '''
        The mouse was moved with one or more mouse buttons pressed.

        This event will stop to be fired if the mouse leaves the figure.

        :Parameters:

           ``x`` : int
               Distance in pixels from the left edge of the figure.

           ``y`` : int
               Distance in pixels from the bottom edge of the figure.

           ``dx`` : int
               Relative X position from the previous mouse position.

           ``dy`` : int
               Relative Y position from the previous mouse position.

           ``button`` : int
               Bitwise combination of the mouse buttons currently pressed.
        '''

        for fig in self._figures:
            if (x,y) in fig:
                invoked = fig.dispatch_event('on_mouse_drag',
                                            x-fig.X, y-fig.Y, dx, dy, button)
                if invoked == EVENT_HANDLED: return invoked
        return EVENT_UNHANDLED


    # ------------------------------------------------------- on_mouse_drag ---
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        '''
        The mouse wheel was scrolled.

        Note that most mice have only a vertical scroll wheel, so `scroll_x` is
        usually 0.

        :Parameters:

            ``x`` : int
                Distance in pixels from the left edge of the figure.

            ``y`` : int
                Distance in pixels from the bottom edge of the figure.

            ``scroll_x`` : int
                Number of "clicks" towards the right (left if negative).

            ``scroll_y`` : int
                Number of "clicks" upwards (downwards if negative).
        '''

        for fig in self._figures:
            if (x,y) in fig:
                invoked = fig.dispatch_event('on_mouse_scroll',
                                            x-fig.X, y-fig.Y, scroll_x, scroll_y)
                if invoked == EVENT_HANDLED: return invoked
        return EVENT_UNHANDLED


    # -------------------------------------------------------------- event ---
    def event(self, *args):
        '''Function decorator for an event handler.'''

        if self.parent is None:
            return EventDispatcher.event(self.root,*args)
        else:
            # If the event is 'on_idle', we attache it directly to the window
            if args[0] == 'on_idle' or args[0].__name__ == 'on_idle':
                self.root.push_handlers(*args)
            else:
                return EventDispatcher.event(self,*args)



# ------------------------------------------------------------------- Frame ---
class Frame(Figure):
    ''' 
    A Frame is a special king of figure that can drawns itself and preserves a
    given aspect ratio.
    '''

    def __init__(self, figure, size = (1.0,1.0), aspect = None,
                 fg_color=(0,0,0,1), bg_color=(1,1,1,1)):
        '''
        Create a new frame within given figures.

        :Parameters:
        
            ``figure``: Figure
                 Figure to put frame into

            ``size``: (float,float)
                 Frame relative size

             ``aspect``: float
                 Frame aspect

             ``fg_color``: 4-floats tuple
                 Foreground color (border)

             ``bg_color``: 4-floats tuple
                 Background color
        '''
        Figure.__init__(self, size=size, parent=figure)
        self._aspect   = aspect
        self._fg_color = fg_color
        self._bg_color = bg_color


    # --------------------------------------------------------------- width ---
    def _get_width(self):
        ''' Get frame width in pixels '''
        W,H = self.parent.width, self.parent.height
        w,h = self._size[0]*W, self._size[1]*H
        if self._aspect is not None:
            if w/float(h) > self._aspect:
                w = self._aspect*h
            else:
                h = w/self._aspect
        return w
    width = property(_get_width,
         doc='''
         Frame width in pixels. Read-only.
         
         :type: int
         ''')
   
    # -------------------------------------------------------------- height ---
    def _get_height(self):
        ''' Get frame height in pixels '''
        W,H = self.parent.width, self.parent.height
        w,h = self._size[0]*W, self._size[1]*H
        if self._aspect is not None:
            if w/float(h) > self._aspect:
                w = self._aspect*h
            else:
                h = w/self._aspect
        return h
    height = property(_get_height,
         doc='''
         Frame height in pixels. Read-only.
         
         :type: int
         ''')

    # ------------------------------------------------------------------- x ---
    def _get_x(self):
        ''' Get frame x coordinate relatively to parent figure origin'''
        W,H = self.parent.width, self.parent.height
        w,h = self.width, self.height
        if self._aspect is not None:
            if w/float(h) > self._aspect:
                w = self._aspect*h
            else:
                h = w/self._aspect
        return (W-w)/2
    x = property(_get_x,
         doc='''
         Figure x coordinate relatively to parent figure origin. Read-only.
         
         :type: int
         ''')


    # ------------------------------------------------------------------- y ---
    def _get_y(self):
        ''' Get frame x coordinate relatively to parent figure origin'''
        W,H = self.parent.width, self.parent.height
        w,h = self.width, self.height
        if self._aspect is not None:
            if w/float(h) > self._aspect:
                w = self._aspect*h
            else:
                h = w/self._aspect
        return (H-h)/2
    y = property(_get_y,
         doc='''
         Frame y coordinate relatively to parent figure origin. Read-only.
         
         :type: int
         ''')



    # ---------------------------------------------------------------- draw ---
    def draw(self, x=0, y=0, z=-999):
        '''
        Draw the frame at specified coordinates.

        :Parameters:

            ``x`` : float
                X coordinate

            ``y`` : float
                Y coordinate

            ``z`` : float
                Z coordinate

        :Note:

            Background is drawn at depth z while foreground border is drawn at
            depth -z.
        '''

        x,y,z = x + .315, y + .315, -abs(z)
        w,h = int(round(self.width))- 1, int(round(self.height)) -1

        gl.glDisable(gl.GL_BLEND)
        gl.glDisable(gl.GL_LINE_SMOOTH)

        gl.glColor(*self._bg_color)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex3f(x,   y,   z)
        gl.glVertex3f(x+w, y,   z)
        gl.glVertex3f(x+w, y+h, z)
        gl.glVertex3f(x,   y+h, z)
        gl.glEnd()

        gl.glColor(*self._fg_color)
        gl.glBegin(gl.GL_LINE_LOOP)
        gl.glVertex3f(x,   y,   -z)
        gl.glVertex3f(x+w, y,   -z)
        gl.glVertex3f(x+w, y+h, -z)
        gl.glVertex3f(x,   y+h, -z)
        gl.glEnd()



Figure.register_event_type('on_init')
Figure.register_event_type('on_resize')
Figure.register_event_type('on_draw')
Figure.register_event_type('on_idle')
# Figure.register_event_type('on_show')
# Figure.register_event_type('on_hide')
# Figure.register_event_type('on_activate')
# Figure.register_event_type('on_deactivate')
Figure.register_event_type('on_key_press')
Figure.register_event_type('on_key_release')
Figure.register_event_type('on_mouse_motion')
Figure.register_event_type('on_mouse_drag')
Figure.register_event_type('on_mouse_press')
Figure.register_event_type('on_mouse_release')
Figure.register_event_type('on_mouse_scroll')
# Figure.register_event_type('on_mouse_enter')
# Figure.register_event_type('on_mouse_leave')
# Figure.register_event_type('on_expose')

