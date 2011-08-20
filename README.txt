Description
===========

glumpy is a small python library for the rapid vizualization of numpy arrays,
(mainly two dimensional) that has been designed with efficiency in mind. If you
want to draw nice figures for inclusion in a scientific article, you'd better
use matplotlib. If you want to have a sense of what's going on in your
simulation while it is running, then glumpy can help you.

Dependencies
-----------
glumpy is made on top of PyOpenGL (http://pyopengl.sourceforge.net/) and since
glumpy is dedicated to numpy visualization, you obviously need numpy
(http://numpy.scipy.org/). You will also need IPython
(http://ipython.scipy.org/) for running interactive sessions where you can
interact with glumpy.

Some demos require matplotlib (http://matplotlib.sourceforge.net/) and scipy
(http://www.scipy.org/) as well but this is optional.

Mailing lists
-------------
The main forum for glumpy discussion is the glumpy-users mailing list at
http://groups.google.com/group/glumpy-users. You can browse the mailing list
online or provide your email address for immediate or digest updates.

How does it work ?
==================
glumpy uses OpenGL textures to represent arrays since it is probably the
fastest method of visualization on modern graphic hardware. However, the
drawback is that it implies some restriction on the type and shape of arrays
that can be visualized using this method. The dtype of array must be one of
numpy.uint8 or numpy.float32 (because on existing restriction on OpenGL
textures data types) and the shape of the array must be one of M, MxN or
MxNx[1,2,3,4]. Apart from pure rendering performances, OpenGL textures offer
the advantage of being able to use shaders that can alter their
rendering. glumpy uses such shaders to implement color lookup table
(i.e. colormap), filtering (nearest / bilinear / bicubic) and displacements
(heightmaps). In other words, rendering is done entirely on the graphic card,
saving CPU time for simulation.

Interactive sessions
--------------------

Thanks to the IPython shell, glumpy can be ran in interactive mode where you
can experience live update in displayed arrays when their contents is changed.

Example usage
-------------


demo-simple.py::

  import numpy, glumpy

  window = glumpy.Window(512,512)
  Z = numpy.random.random((32,32)).astype(numpy.float32)
  I = glumpy.Image(Z, interpolation='nearest', cmap=glumpy.colormap.Grey)

  @window.event
  def on_draw():
      window.clear()
      I.blit(0,0,window.width,window.height)

  window.mainloop()
