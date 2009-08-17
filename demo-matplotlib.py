#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# glumpy - Fast OpenGL numpy visualization
# Copyright (c) 2009 - Nicolas P. Rougier
#
# This file is part of glumpy.
#
# glumpy is free  software: you can redistribute it and/or  modify it under the
# terms of  the GNU General  Public License as  published by the  Free Software
# Foundation, either  version 3 of the  License, or (at your  option) any later
# version.
#
# glumpy is  distributed in the  hope that it  will be useful, but  WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy  of the GNU General Public License along with
# glumpy. If not, see <http://www.gnu.org/licenses/>.
#
# -----------------------------------------------------------------------------
import pyglet
pyglet.options['debug_gl'] = False
import pyglet.gl as gl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import glumpy

from matplotlib.backend_bases import NavigationToolbar2

transparent = np.array([1,2,3,255])
items = []
frame = None



class NavigationToolbar(NavigationToolbar2):
    def __init__(self, canvas, window):
        self.window = window
        self.message = pyglet.text.Label(text='',
                                         font_name='Monaco', font_size=12,
                                         x=window.width, y=0,
                                         color = (127,127,127,127),
                                         anchor_x='right', anchor_y='top')
        NavigationToolbar2.__init__(self, canvas)

    def _init_toolbar(self):
        pass

    def set_message(self, s):
        self.message.text = s
        self.message.x = self.window.width
        self.message.y = self.window.height

    def draw(self):
        self.message.draw()


def savefig (filename, width, height):
    ''' Save viewport to a bitmap file '''

    viewport = (gl.GLint*4)()
    gl.glGetIntegerv(gl.GL_VIEWPORT, viewport)

    # Setup framebuffer
    framebuffer = gl.GLuint()
    gl.glGenFramebuffersEXT(1, framebuffer)
    if not framebuffer.value:
        raise RuntimeError('Cannot create framebuffer')
    gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, framebuffer)

    # Setup depthbuffer
    depthbuffer = gl.GLuint()
    gl.glGenRenderbuffersEXT(1, depthbuffer)
    gl.glBindRenderbufferEXT (gl.GL_RENDERBUFFER_EXT, depthbuffer)
    gl.glRenderbufferStorageEXT (gl.GL_RENDERBUFFER_EXT,
                                 gl.GL_DEPTH_COMPONENT, width, height)

    # Create texture to render to
    texture = gl.GLuint()
    gl.glGenTextures(1, gl.byref(texture))
    gl.glBindTexture (gl.GL_TEXTURE_2D, texture)
    gl.glTexParameteri (gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri (gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D (gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0,
                     gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, 0)
    gl.glFramebufferTexture2DEXT (gl.GL_FRAMEBUFFER_EXT,
                                  gl.GL_COLOR_ATTACHMENT0_EXT,
                                  gl.GL_TEXTURE_2D, texture, 0);
    gl.glFramebufferRenderbufferEXT(gl.GL_FRAMEBUFFER_EXT,
                                    gl.GL_DEPTH_ATTACHMENT_EXT, 
                                    gl.GL_RENDERBUFFER_EXT, depthbuffer);
    status = gl.glCheckFramebufferStatusEXT (gl.GL_FRAMEBUFFER_EXT);
    if status != gl.GL_FRAMEBUFFER_COMPLETE_EXT:
        raise RuntimeError('Error in framebuffer activation')

    # Resize, render & save
    data = (gl.GLubyte * (width*height*4))()
    gl.glViewport(0,0,width,height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glOrtho(0, width, 0, height, -1, 1)
    gl.glClearColor(1,1,1,0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    for image,axis,alpha in items:
        x,y,w,h = axis.get_axes().bbox.bounds
        x /= float(frame.shape[1])
        y /= float(frame.shape[0])
        w /= float(frame.shape[1])
        h /= float(frame.shape[0])
        gl.glColor4f(1,1,1,alpha)
        image.blit(x*width,y*height, w*width,h*height)
    gl.glColor4f(1,1,1,1)
    frame.blit(0,0,width,height)

    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glReadPixels(0, 0, width, height, gl.GL_RGBA,
                    gl.GL_UNSIGNED_BYTE, gl.byref(data))
    image = pyglet.image.ImageData(width, height, 'RGBA', data)
    image.save(filename)

    # Cleanup
    gl.glBindRenderbufferEXT (gl.GL_RENDERBUFFER_EXT, 0)
    gl.glBindFramebufferEXT (gl.GL_FRAMEBUFFER_EXT, 0)
    gl.glDeleteTextures (1, texture)
    gl.glDeleteFramebuffersEXT(1,framebuffer)

    # Restoring previous viewport
    x,y,w,h = viewport
    gl.glViewport(x,y,w,h)



def imshow(X, cmap=None, norm=None, aspect=None, interpolation=None,
           alpha=1.0, vmin=None, vmax=None, origin=None, extent=None,
           **kwargs):

    '''pylab imshow proxy function.

       This function first call the pylab original imshow function using an
       alpha level of 0 (fully transparent). It then set axes background with a
       dedicated 'transparent' color that will be replaced later by a truly
       transparent color.

       Warning: any pixel with 'transparent' color will be replaced by a
                transparent pixel. If this causes problem, you will have to
                change the definition of 'transparent' to something else.
    '''
    axis = plt.imshow(X, cmap=cmap, norm=norm, aspect=aspect,
                      interpolation='nearest', alpha=0, vmin=vmin,
                      vmax=vmax, origin=origin, extent=extent, **kwargs)

    r,g,b,a = transparent/255.0
    cmap = axis.cmap
    under = cmap(-1.0)
    over = cmap(2.0)
    axis.cmap.set_over((r,g,b), alpha=0)
    axis.cmap.set_under((r,g,b), alpha=0)
    axis.cmap.set_bad((r,g,b), alpha=0)
    axes = axis.get_axes()
    axes.patch.set_facecolor((r,g,b))
    axes.patch.set_alpha(a)

    # Build glumpy colormap from matplotlib colormap
    colors=[]
    for i in range(510):
        colors.append((i/510.0, cmap(i/510.0, alpha=alpha)))
    cmap = glumpy.colormap.Colormap(*colors, over=glumpy.Color(over), under=glumpy.Color(under))
    image = glumpy.Image(X,interpolation=interpolation, cmap=cmap, vmin=vmin, vmax=vmax)
    image.update()
    items.append([image,axis,alpha])
    return axis


def show(interpolation='nearest'):
    ''' pylab show proxy function. '''
    global frame


    # Draw current figure to rgba buffer
    fig = plt.gcf()
    fig.canvas.draw()
    buffer = fig.canvas.buffer_rgba(0,0)
    x,y,w,h = fig.bbox.bounds
    F = np.fromstring(buffer,np.uint8).copy()
    F.shape = h,w,4

    # Replace 'transparent' color with a real transparent color
    v = np.array(transparent,dtype=np.uint8).view(dtype=np.int32)[0]
    Ft = np.where(F.view(dtype=np.int32) == v, 0, F)

    # Create main frame 
    frame = glumpy.Image(Ft,interpolation=interpolation)
    frame.update()

    window = pyglet.window.Window(frame.shape[1], frame.shape[0],
                                  vsync=0, resizable=True)


    fig_manager = plt.get_current_fig_manager()
    canvas = fig_manager.canvas

    toolbar = NavigationToolbar(canvas, window)
    def notify_axes_change(fig):
        fig_manager.toolbar.update()
    fig_manager.canvas.figure.add_axobserver(notify_axes_change)

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    #fps_display = pyglet.clock.ClockDisplay()



    @window.event
    def on_resize(width,height):
        global frame

        fig = plt.gcf()
        dpi = float(fig.dpi)
        winch = width/dpi
        hinch = height/dpi
        fig.set_size_inches(winch, hinch)

        fig.canvas.draw()
        buffer = fig.canvas.buffer_rgba(0,0)
        x,y,w,h = fig.bbox.bounds
        
        F = np.fromstring(buffer,np.uint8).copy()
        F.shape = h,w,4
        # Replace 'transparent' color with a real transparent color
        v = np.array(transparent,dtype=np.uint8).view(dtype=np.int32)[0]
        Ft = np.where(F.view(dtype=np.int32) == v, 0, F)
        # Create main frame 
        frame = glumpy.Image(Ft,interpolation=interpolation)
        frame.update()


    @window.event
    def on_mouse_motion(x, y, buttons, modifiers):
        fig_manager = plt.get_current_fig_manager()
        fig_manager.canvas.motion_notify_event(x, y)
        return True

    @window.event
    def on_draw():
        window.clear()
        for image,axis, alpha in items:
            x,y,w,h = axis.get_axes().bbox.bounds
            x /= float(frame.shape[1])
            y /= float(frame.shape[0])
            w /= float(frame.shape[1])
            h /= float(frame.shape[0])
            gl.glColor4f(1,1,1,alpha)
            image.blit(x*window.width,y*window.height,
                       w*window.width,h*window.height)
        gl.glColor4f(1,1,1,1)
        frame.blit(0,0,window.width, window.height)
        fig_manager = plt.get_current_fig_manager()
        toolbar.draw()
        #fps_display.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            savefig('test.png', window.width, window.height)
        if symbol == pyglet.window.key.ESCAPE:
            if window.width == frame.shape[1] and window.height == frame.shape[0]:
                pyglet.app.exit()
            else:
                window.set_size(frame.shape[1], frame.shape[0])
            return True
    pyglet.app.run()






def func3(x,y):
    return (1-x/2+x**5+y**3)*np.exp(-x**2-y**2)
dx, dy = .05, .05
x = np.arange(-3.0, 3.0, dx, dtype=np.float32)
y = np.arange(-3.0, 3.0, dy, dtype=np.float32)
Z = func3(*np.meshgrid(x, y))


fig = plt.figure(figsize=(7,7), facecolor='.9')
plt.suptitle('''Generated using matplotlib,\n'''
             '''Displayed using glumpy !''', fontsize=16)
ax = plt.subplot(111)
cmap = plt.cm.hot
cmap.set_under((0,0,1))
cmap.set_over((0,1,0))
ax = imshow(Z, origin='lower', interpolation='bicubic', cmap=cmap,
            extent=[0,Z.shape[0],0,Z.shape[1]], vmin=-0.5, vmax=0.5)
# Does not work yet
#plt.colorbar()
plt.grid()


show() #'bicubic')

