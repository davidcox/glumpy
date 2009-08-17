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
#
# This code has been mostly adapted from the callproxy.py script of the PLI
# library by Alex A. Naanou (http://pli.sourceforge.net)
# Sources available at http://repo.or.cz/w/pli.git
#
# -----------------------------------------------------------------------------
import sys
import new
import types
import _ctypes
import weakref
import pyglet
pyglet.options['debug_gl'] = False
import pyglet.gl as gl
import traceback
import threading
import IPython.ipapi
from functools import partial


class Proxy(object):
    '''
    proxy to the object, intercept and curry all calls to a queue.
    '''

    def __new__(cls, obj, queue, cache=None):
        '''
        Construct an appropriate class and return its object, the class is to be
        a subclass of Proxy and the object class. If this is to prove impossible
        return the original object or a curried __queuecall__ if the object is
        callable.

        :Parameters:
	    `obj` : object
                object to be proxied
            `queue` : list
                optional list to be used as an external queue.
            `cache` : dict
                optional dict to be used as proxy cache 
        '''

        if cache != None and obj in cache.keys():
            proxy = object.__getattribute__(cache[obj], '__class__')
            if queue != None and type(obj) in (types.FunctionType,
                                               types.LambdaType,
                                               types.MethodType,
                                               weakref.CallableProxyType):
                return partial(cls.__queuecall__, obj, queue)
            return cache[obj]

        try:
            _obj = object.__new__(new.classobj('T',(Proxy, obj.__class__), {}))
            cls = object.__getattribute__(_obj, '__class__')
            object.__setattr__(_obj, '__dict__', obj.__dict__)
            cls._proxy_object = obj
            cls._proxy_queue = queue
            cls._proxy_cache = cache
            if cache != None:
                cache[obj] = _obj
        except (TypeError, AttributeError):
            # function or callable
            if type(obj) in (types.FunctionType,
                             types.LambdaType,
                             types.MethodType,
                             weakref.CallableProxyType):
                if cache != None:
                    cache[obj] = partial(cls.__queuecall__, obj,queue)
                    return cache[obj]
                return partial(cls.__queuecall__, obj, queue)
            # class (nested class constructors...)
            elif callable(obj):
                return obj
            return obj
        return _obj

    
    def __init__(self, *args, **kwargs):
        ''' Necessary dummy init '''
        pass


    def __getattribute__(self, name):
        get = object.__getattribute__
        cls = get(self, '__class__')
        if name == '__queuecall__':
            return get(self, '__queuecall__')
        return Proxy(getattr(cls._proxy_object, name), cls._proxy_queue, cls._proxy_cache)


    def __setattr__(self, name, val):
        cls = object.__getattribute__(self, '__class__')
        cls.__queuecall__(setattr, cls._proxy_queue, cls._proxy_object, name, val)


    def __delattr__(self, name):
        cls = object.__getattribute__(self, '__class__')
        cls.__queuecall__(delattr, cls._proxy_queue, cls._proxy_object, name)
        #delattr(cls._proxy_object, name)


    def __queuecall__(obj, queue, *args, **kwargs):
        queue.push(obj,args,kwargs)
    __queuecall__ = staticmethod(__queuecall__)


    def __call__(self, *args, **kwargs):
        get = object.__getattribute__
        cls = get(self, '__class__')
        obj = get(cls, '_proxy_object')
        if not callable(obj):
            # raise an error disguised as the original
            obj(args, kwargs)
        queue = cls._proxy_queue
        cls.__queuecall__(*(obj, queue) + args, **kwargs)
        return



class App(object):

    def __init__ (self):
        self.lock = threading.Lock()
        self.queue = []

    def push(self, obj, args, kwargs):
        ''' Push a new object call onto the stack '''
        class container(object):
            def __init__(self):
                self.value = None
                self.filled = False
            def __call__(self, value=None):
                self.value = value
                self.filled = True
        output = container()
        self.lock.acquire()
        self.queue.append((obj, args, kwargs, output))
        self.lock.release()
        while not output.filled: pass
        return output.value

    def pop(self, dt=0):
        ''' Process one object call from the stack '''

        if not len(self.queue): return
        self.lock.acquire()
        function, args, kwargs, output = self.queue.pop(0)
        self.lock.release()
        
        try:
            result = function(*args,**kwargs)
        except:
            traceback.print_exc()
            result = None
        if output:
            output(result)

    def run(self, namespace=None, interval=1/60.):
        ''' ''' 

        # Creates proxies for all (supposed) gl functions
        namespace = namespace.copy()
        for key in namespace.keys():
            f = namespace[key]
            if key[:2] == 'gl' and isinstance(namespace[key], _ctypes.CFuncPtr):
                namespace[key] = Proxy(f, app)
        def session_start():
            IPython.ipapi.launch_new_instance(namespace)
            pyglet.app.exit()
        session = threading.Thread(target=session_start)
        session.start()
        while session.isAlive():
            pyglet.clock.schedule_interval(self.pop, interval)
            pyglet.app.run()
            pyglet.clock.unschedule(self.pop)
            

app = App()
def proxy(obj,app=app):
    return Proxy(obj,app)

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import pyglet

    _window = pyglet.window.Window(vsync=0)
    @_window.event
    def on_draw():
        _window.clear()
    window = Proxy(_window, app)
    app.run(namespace=globals())
