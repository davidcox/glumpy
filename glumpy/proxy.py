#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (C) 2009-2010  Nicolas P. Rougier
#
# Distributed under the terms of the BSD License. The full license is in
# the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
#
# This code has been mostly adapted from the callproxy.py script of the PLI
# library by Alex A. Naanou (http://pli.sourceforge.net)
# Sources available at http://repo.or.cz/w/pli.git
#
# -----------------------------------------------------------------------------
import new
import types
import weakref
import threading
from functools import partial


# -----------------------------------------------------------------------------
class Proxy(object):
    '''
    proxy of the object, intercept and curry all calls to a queue.
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
            if (queue != None and
                isinstance(obj, types.FunctionType) or
                isinstance(obj, types.MethodType) or
                isinstance(obj, types.LambdaType) or
                isinstance(obj, weakref.CallableProxyType) or
                type(obj).__name__ in ['CFunctionType']):
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
            if (isinstance(obj, types.FunctionType) or
                isinstance(obj, types.MethodType) or
                isinstance(obj, types.LambdaType) or
                isinstance(obj, weakref.CallableProxyType) or
                type(obj).__name__ in ['CFunctionType']):
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
        return Proxy(getattr(cls._proxy_object, name),
                     cls._proxy_queue, cls._proxy_cache)


    def __setattr__(self, name, val):
        cls = object.__getattribute__(self, '__class__')
        cls.__queuecall__(setattr, cls._proxy_queue,
                          cls._proxy_object, name, val)


    def __delattr__(self, name):
        cls = object.__getattribute__(self, '__class__')
        cls.__queuecall__(delattr, cls._proxy_queue,
                          cls._proxy_object, name)
        #delattr(cls._proxy_object, name)


    def __queuecall__(obj, queue, *args, **kwargs):
        queue._push(obj,args,kwargs)
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

