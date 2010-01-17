import logging
import datetime
from google.appengine.api import users, memcache
from google.appengine.ext import db
from helpers import HandlerBase, create_user, each_profiles
from models.profile import Profile
from models.follow import Follow
from models.blip import Blip, BlipLink, PublicTimeView
import settings

class BuildBlipLink(HandlerBase):
    def get(self):
        cnt = 0
        for bl in BlipLink.all():
            bl.date_blip_created = bl.blip.date_created
            bl.put()
            cnt += 1
        self.response.out.write('build %s blip links' % cnt)

class CleanCache(HandlerBase):
    def get(self):
        memcache.flush_all()
        self.response.out.write('OK')
