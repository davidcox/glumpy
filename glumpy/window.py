#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
# -----------------------------------------------------------------------------
import sys, time
import atexit
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import key, mouse, event, proxy
import _ctypes
import threading
import traceback
import IPython

if sys.platform in ['linux2', 'darwin']:
    import termios

# The one and only window
_window = None

def active_window():
    return _window


class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
         if cls._instance is None:
             cls._instance = object.__new__(cls)
         return cls._instance

class Window(event.EventDispatcher, Singleton):

    # Instance variables accessible only via properties
    _fullscreen = False
    _visible = False

    # Subclasses should update these after relevant events
    _mouse_x = 0
    _mouse_y = 0
    _button = mouse.NONE
    _modifiers = None
    _mouse_in_window = False
    _event_queue = None
    _time = None
    _width = None
    _height = None
    _window_id = None
    _timer_stack = []
    _timer_date = []
    _lock = threading.Lock()
    _command_queue = []

    # Class attributes
    _default_width = 640
    _default_height = 480


    def __init__(self, width=None, height=None, caption=None, visible=True, fullscreen=False):

        event.EventDispatcher.__init__(self)

        self._event_queue = []
        if width and width > 0:
            self._width = width
        else:
            self._width = Window._default_width
        if height and height > 0:
            self._height = height
        else:
            self._height = Window._default_height
        if caption is None:
            caption = sys.argv[0]
        self._caption = caption

        self._saved_width  = self._width
        self._saved_height = self._height

        if _window is None:
            glut.glutInit(sys.argv)
            glut.glutInitDisplayMode(glut.GLUT_DOUBLE |
                                     glut.GLUT_RGBA   |
                                     glut.GLUT_DEPTH)
            self._window_id = glut.glutCreateWindow(self._caption)
        glut.glutDisplayFunc(self._display)
        glut.glutReshapeFunc(self._reshape)
        glut.glutKeyboardFunc(self._keyboard)
        glut.glutKeyboardUpFunc(self._keyboard_up)
        glut.glutMouseFunc(self._mouse)
        glut.glutMotionFunc(self._motion)
        glut.glutPassiveMotionFunc(self._passive_motion)
        glut.glutVisibilityFunc(self._visibility)
        glut.glutEntryFunc(self._entry)
        glut.glutSpecialFunc(self._special)
        glut.glutSpecialUpFunc(self._special_up)
        gl.glClearColor(0,0,0,0)
        self._visible = visible
        self._time = glut.glutGet(glut.GLUT_ELAPSED_TIME)
        if not visible:
            glut.glutHideWindow()
        else:
            glut.glutShowWindow()
        self.set_size(self._width, self._height)
        screen_width = glut.glutGet(glut.GLUT_SCREEN_WIDTH)
        screen_height= glut.glutGet(glut.GLUT_SCREEN_HEIGHT)
        glut.glutPositionWindow((screen_width-self._width)//2,
                                (screen_height-self._height)//2)
        self.fullscreen = fullscreen


    def _keyboard(self, code, x, y):
         symbol = self._keyboard_translate(code)
         modifiers = glut.glutGetModifiers()
         modifiers = self._modifiers_translate(modifiers)
         state= self.dispatch_event('on_key_press', symbol, modifiers)
         if not state and symbol == key.ESCAPE:
             sys.exit()

    def _keyboard_up(self, code, x, y):
        modifiers = glut.glutGetModifiers()
        self.dispatch_event('on_key_release',
                            self._keyboard_translate(code),
                            self._modifiers_translate(modifiers))

    def _special(self, code, x, y):
        modifiers = glut.glutGetModifiers()
        self.dispatch_event('on_key_press',
                            self._keyboard_translate(code),
                            self._modifiers_translate(modifiers))

    def _special_up(self, code, x, y):
        modifiers = glut.glutGetModifiers()
        self.dispatch_event('on_key_release',
                            self._keyboard_translate(code),
                            self._modifiers_translate(modifiers))

    def _modifiers_translate(self, modifiers):
        _modifiers = 0
        if modifiers & glut.GLUT_ACTIVE_SHIFT:
            _modifiers |=  key.MOD_SHIFT
        if modifiers & glut.GLUT_ACTIVE_CTRL:
            _modifiers |=  key.MOD_CTRL
        if modifiers & glut.GLUT_ACTIVE_ALT:
            _modifiers |=  key.MOD_ALT
        return _modifiers

    def _keyboard_translate(self, code):
        ascii = ord(code.lower())
        if (0x020 <= ascii <= 0x040) or (0x05b <= ascii <= 0x07e):
            return ascii
        elif ascii < 0x020:
            if   ascii == 0x008: return key.BACKSPACE
            elif ascii == 0x009: return key.TAB
            elif ascii == 0x00A: return key.LINEFEED
            elif ascii == 0x00C: return key.CLEAR
            elif ascii == 0x00D: return key.RETURN
            elif ascii == 0x018: return key.CANCEL
            elif ascii == 0x01B: return key.ESCAPE
        elif code==glut.GLUT_KEY_F1:       return key.F1
        elif code==glut.GLUT_KEY_F2:       return key.F2
        elif code==glut.GLUT_KEY_F3:       return key.F3
        elif code==glut.GLUT_KEY_F4:       return key.F4
        elif code==glut.GLUT_KEY_F5:       return key.F5
        elif code==glut.GLUT_KEY_F6:       return key.F6
        elif code==glut.GLUT_KEY_F7:       return key.F7
        elif code==glut.GLUT_KEY_F8:       return key.F8
        elif code==glut.GLUT_KEY_F9:       return key.F9
        elif code==glut.GLUT_KEY_F10:      return key.F10
        elif code==glut.GLUT_KEY_F11:      return key.F11
        elif code==glut.GLUT_KEY_F12:      return key.F12
        elif code==glut.GLUT_KEY_LEFT:     return key.LEFT
        elif code==glut.GLUT_KEY_UP:       return key.UP
        elif code==glut.GLUT_KEY_RIGHT:    return key.RIGHT
        elif code==glut.GLUT_KEY_DOWN:     return key.DOWN
        elif code==glut.GLUT_KEY_PAGE_UP:  return key.PAGEUP
        elif code==glut.GLUT_KEY_PAGE_DOWN:return key.PAGEDOWN
        elif code==glut.GLUT_KEY_HOME:     return key.HOME
        elif code==glut.GLUT_KEY_END:      return key.END
        elif code==glut.GLUT_KEY_INSERT:   return key.INSERT


    def _display(self):
        #self.clear()
        self.dispatch_event('on_draw')
        self.flip()

    def _idle(self):
        t = glut.glutGet(glut.GLUT_ELAPSED_TIME)
        dt = (t - self._time)/1000.0
        self._time = t
        self.dispatch_event('on_idle', dt)

    def _reshape(self, width, height):
        width  = glut.glutGet(glut.GLUT_WINDOW_WIDTH)
        height = glut.glutGet(glut.GLUT_WINDOW_HEIGHT)
        self._width, self._height = width, height
        self.dispatch_event('on_resize', self._width, self._height)
        #glut.glutPostRedisplay()

    def _visibility(self, state):
        if state == glut.GLUT_VISIBLE:
            self._visible = True
            self.dispatch_event('on_show')
            glut.glutPostRedisplay()
        elif state == glut.GLUT_NOT_VISIBLE:
            self._visible = False
            self.dispatch_event('on_hide')

    def _entry(self, state):
        if state == glut.GLUT_ENTERED:
            self._mouse_in_window = True
            self.dispatch_event('on_mouse_enter')
        elif state == glut.GLUT_LEFT:
            self._mouse_in_window = False
            self.dispatch_event('on_mouse_leave')

    def _mouse(self, button, state, x, y):
        y = self._height - y

        if button == glut.GLUT_LEFT_BUTTON:
            button = mouse.LEFT
        elif button == glut.GLUT_MIDDLE_BUTTON:
            button = mouse.MIDDLE
        elif button == glut.GLUT_RIGHT_BUTTON:
            button = mouse.RIGHT
        if state == glut.GLUT_UP:
            self._button = mouse.NONE
            self._mouse_x = x
            self._mouse_y = y
            self.dispatch_event('on_mouse_release', x, y, button)
        elif state == glut.GLUT_DOWN:
            self._button = button
            self._mouse_x = x
            self._mouse_y = y
            if button == 3:
                self._button = mouse.NONE
                self.dispatch_event('on_mouse_scroll', x, y, 0, 1)
            elif button == 4:
                self._button = mouse.NONE
                self.dispatch_event('on_mouse_scroll', x, y, 0, -1)
            else:
                self.dispatch_event('on_mouse_press', x, y, button)

    def _motion(self, x, y):
        y = self._height - y

        dx = x - self._mouse_x
        dy = y - self._mouse_y
        self._mouse_x = x
        self._mouse_y = y
        self.dispatch_event('on_mouse_drag', x, y, dx, dy, self._button)

    def _passive_motion(self, x, y):
        y = self._height - y

        dx = x - self._mouse_x
        dy = y - self._mouse_y
        self._mouse_x = x
        self._mouse_y = y
        self.dispatch_event('on_mouse_motion', x, y, dx, dy)


    def _push(self, obj, args, kwargs):
        ''' Push a new object call onto the stack '''

        class container(object):
            def __init__(self):
                self.value = None
                self.filled = False
            def __call__(self, value=None):
                self.value = value
                self.filled = True
        output = container()
        self._lock.acquire()
        self._command_queue.append((obj, args, kwargs, output))
        self._lock.release()
        while not output.filled: pass
        return output.value


    def _pop(self, value):
        ''' Process one object call from the stack '''

        if not len(self._command_queue):
            glut.glutTimerFunc(100, self._pop, 0)
            return True
        self._lock.acquire()
        function, args, kwargs, output = self._command_queue.pop(0)
        self._lock.release()
        try:
            result = function(*args,**kwargs)
        except:
            traceback.print_exc()
            result = None
        if output:
            output(result)
        glut.glutTimerFunc(100, self._pop, 0)
        glut.glutPostRedisplay()
        return True


    def mainloop(self, interactive=False, namespace=globals()):
        '''Starts main loop
        '''

        # Start timers
        for i in range(len(self._timer_stack)):
            def func(index):
                handler, fps = self._timer_stack[index]
                t = glut.glutGet(glut.GLUT_ELAPSED_TIME)
                dt = (t - self._timer_date[index])/1000.0
                self._timer_date[index] = t
                handler(dt)
                glut.glutTimerFunc(int(1000./fps), func, index)
                self._timer_date[index] = glut.glutGet(glut.GLUT_ELAPSED_TIME)
            fps = self._timer_stack[i][1]
            glut.glutTimerFunc(int(1000./fps), func, i)

        # Start idle only if necessary
        for item in self._event_stack:
            if 'on_idle' in item.keys():
                glut.glutIdleFunc(self._idle)

        self.dispatch_event('on_init')

        # Starts non-interactive mode
        if not interactive:
            glut.glutMainLoop()
            sys.exit()

        # Starts interactive mode
        # Save tty mode on linux/darwin
        if sys.platform in ['linux2', 'darwin']:
            self.term_state = termios.tcgetattr(sys.stdin)
        namespace = namespace.copy()
        for key in namespace.keys():
            f = namespace[key]
            if key[:2] == 'gl' and isinstance(namespace[key], _ctypes.CFuncPtr):
                namespace[key] = proxy.Proxy(f,self)
        def session_start():
            self.shell = IPython.ipapi.make_session(namespace)
            self.shell.IP.interact() #mainloop()
            sys.exit()
        self.session = threading.Thread(target=session_start)
        self.session.start()

        @atexit.register
        def goodbye():
            self.shell.IP.ask_exit()
            # Restore tty state on linux/darwin
            if sys.platform in ['linux2', 'darwin']:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.term_state)
            sys.stdout.write('\n')
        glut.glutTimerFunc(100, self._pop, 0)
        glut.glutMainLoop()


    def get_fullscreen(self):
        ''' Get fullscreen mode '''
        return self._fullscreen


    def set_fullscreen(self, state):
        ''' Exit fullscreen mode '''
        self._fullscreen = state
        if state:
            self._saved_width  = glut.glutGet(glut.GLUT_WINDOW_WIDTH)
            self._saved_height = glut.glutGet(glut.GLUT_WINDOW_HEIGHT)
            glut.glutFullScreen()
        else:
            glut.glutReshapeWindow(self._saved_width, self._saved_height)


    def exit(self):
        '''Exit mainloop'''
        if (glut.glutLeaveMainLoop):
            glut.glutLeaveMainLoop()
        else:
            sys.exit();

    def timer(self, *args):
        '''Function decorator for a timed handler.
        
        Usage::

            win = window.Window()

            @win.timer(60)
            def timer(dt):
                # ...

        '''

        if len(args) != 1: return
        if type(args[0]) not in (int,float): return
        fps = args[0]
        def decorator(func):
            self._timer_stack.append((func, fps))
            self._timer_date.append(0)
            return func
        return decorator


    def set_size(self, width, height):
        '''Resize the window.
        
        The behaviour is undefined if the window is not resizable, or if
        it is currently fullscreen.

        The window size does not include the border or title bar.

        :Parameters:
            `width` : int
                New width of the window, in pixels.
            `height` : int
                New height of the window, in pixels.

        '''
        glut.glutReshapeWindow(width,height)


    def get_size(self):
        '''Return the current size of the window.

        The window size does not include the border or title bar.

        :rtype: (int, int)
        :return: The width and height of the window, in pixels.
        '''
        width  = glut.glutGet(glut.GLUT_WINDOW_WIDTH)
        height = glut.glutGet(glut.GLUT_WINDOW_HEIGHT)
        return width,height

    def clear(self):
        '''Clear the window.

        This is a convenience method for clearing the color and depth
        buffer.  The window must be the active one (see `switch_to`).
        '''
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)


    def draw(self):
        '''Draw the window.

        This is a convenience method for forcing a redraw. The window must be
        the active one (see `switch_to`).
        '''
        
        glut.glutPostRedisplay()


    def flip(self):
        '''Swap the OpenGL front and back buffers.

        Call this method on a double-buffered window to update the
        visible display with the back buffer. The contents of the back buffer
        is undefined after this operation.

        Windows are double-buffered by default.  This method is called
        automatically by `EventLoop` after the `on_draw` event.
        '''
        glut.glutSwapBuffers()


    def on_resize(self, width, height):
        '''A default resize event handler.

        This default handler updates the GL viewport to cover the entire
        window and sets the ``GL_PROJECTION`` matrix to be orthogonal in
        window space.  The bottom-left corner is (0, 0) and the top-right
        corner is the width and height of the window in pixels.

        Override this event handler with your own to create another
        projection, for example in perspective.
        '''
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, width, 0, height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)


    # These are the only properties that can be set
    fullscreen = property(get_fullscreen,
                          set_fullscreen,
         doc='''Fullscreen mode.
         
         :type: bool
         ''')

    width = property(lambda self: self.get_size()[0],
                     lambda self, width: self.set_size(width, self.height),
         doc='''The width of the window, in pixels.  Read-write.
         
         :type: int
         ''')

    height = property(lambda self: self.get_size()[1],
                      lambda self, height: self.set_size(self.width, height),
         doc='''The height of the window, in pixels.  Read-write.
         
         :type: int
         ''')


Window.register_event_type('on_key_press')
Window.register_event_type('on_key_release')
Window.register_event_type('on_mouse_motion')
Window.register_event_type('on_mouse_drag')
Window.register_event_type('on_mouse_press')
Window.register_event_type('on_mouse_release')
Window.register_event_type('on_mouse_scroll')
Window.register_event_type('on_mouse_enter')
Window.register_event_type('on_mouse_leave')
Window.register_event_type('on_expose')
Window.register_event_type('on_resize')
Window.register_event_type('on_move')
# Window.register_event_type('on_activate')
# Window.register_event_type('on_deactivate')
Window.register_event_type('on_show')
Window.register_event_type('on_hide')
Window.register_event_type('on_draw')
Window.register_event_type('on_idle')
Window.register_event_type('on_init')
_window = Window(1,1,visible=False)
