###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

from google.appengine.api import memcache
from datetime import datetime, timedelta

class CommonMixin(object):
    def put(self):
        self.date_modified = datetime.now()
        self.before_put()
        obj = super(CommonMixin, self).put()
        memcache.set('k:%s' % self.key(), self)
        self.after_put()
        return obj

    def before_put(self):
        pass

    def after_put(self):
        pass

    def delete(self):
        self.before_delete()
        memcache.delete('k:%s' % self.key())
        ret = super(CommonMixin, self).delete()
        self.after_delete()
        return ret

    def before_delete(self):
        pass
    def after_delete(self):
        pass

class CacheView(object):
    def get_key_name(self):
        pass

    def get(self):
        keyname = self.get_key_name()
        obj = memcache.get(keyname)
        if obj:
            return obj
        obj = self.load()
        if obj:
            memcache.set(keyname, obj, 1800)
        return obj

    def load(self):
        pass

    def put(self):
        keyname = self.get_key_name()
        obj = self.load()
        if obj:
            memcache.set(keyname, obj, 1800)
        else:
            memcache.delete(keyname)

    def delete(self):
        keyname = self.get_key_name()
        memcache.delete(keyname)
