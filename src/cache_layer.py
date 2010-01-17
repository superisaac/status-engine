###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import sys, os
import logging
from google.appengine.api import memcache
from google.appengine.ext import db

def cache_decorator(get_func):
    def cached_get(key):
        obj = memcache.get('k:%s' % key)
        if obj:
            return obj
        obj = get_func(key)
        memcache.set('k:%s' % key, obj, 900)
        return obj
    return cached_get

def install():
    db = sys.modules['google.appengine.ext.db']
    db.get = cache_decorator(db.get)

def cache_class_decorator(get_func):
    def _cached_get(cls, key):
        obj = memcache.get('k:%s' % key)
        if obj:
            return obj
        obj = get_func(key)
        memcache.set('k:%s' % key, obj, 900)
        return obj
    return _cached_get

def register(kind):
    kind.get = classmethod(cache_class_decorator(kind.get))

