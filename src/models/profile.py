###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import logging
import random
import datetime
import hashlib
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.api import users
from models.image import AvatarImage
from models.blip import Blip
from mixins import CommonMixin, CacheView
import settings

auth_domain = 'abc.com'
salt = '8371'
session_salt = '6168'

class UserAuth(CommonMixin, db.Model):
    email = db.EmailProperty(required=True)
    password = db.StringProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)
    session_key = db.StringProperty()
    
    @classmethod
    def new(cls, email):
        u = cls(email=email)
        u.gen_session()
        return u

    @classmethod
    def get_by_session(cls, session_key):
        assert session_key is not None
        mc_key = 's_%s' % session_key
        u = memcache.get(mc_key)
        if u:
            return u
        u = cls.gql('WHERE session_key = :1', session_key).get()
        if u:
            u.touch_session()
        return u

    def touch_session(self):
        if self.session_key:
            mc_key = 's_%s' % self.session_key
            memcache.set(mc_key, self, 900) # 15 minutes

    def gen_session(self):
        self.session_key = self._encrypt(self.email, random.random())
        
    def get_user(self):
        u = users.User(email=self.email,
                       _auth_domain=auth_domain,
                       _user_id=str(self.key()))
        u.source = 'local'
        return u

    def _encrypt(self, password, psalt=salt):
        s = hashlib.sha1()
        s.update('%s:%s' % (password, psalt))
        return s.hexdigest()

    def set_password(self, password):
        self.password = self._encrypt(password)
        self.put()

    def check_password(self, password):
        return self.password == self._encrypt(password)

class ProfileByEmailView(CacheView):
    def __init__(self, email):
        self.email = email

    def get_key_name(self):
        return 'pe:%s' % self.email

    def load(self):
        return Profile.gql('WHERE user_email = :1', self.email).get()

class ProfileByNickView(CacheView):
    def __init__(self, nickname):
        self.nickname = nickname

    def get_key_name(self):
        return 'pn:%s' % self.nickname

    def load(self):
        return Profile.gql('WHERE nickname = :1', self.nickname).get()

class Profile(CommonMixin, db.Model):
    user_email = db.EmailProperty()
    is_active = db.BooleanProperty(default=True)
    source = db.StringProperty()
    nickname = db.StringProperty()
    fullname = db.StringProperty()
    has_edited = db.BooleanProperty(default=False)
    avatar = db.ReferenceProperty(AvatarImage)
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_modified = db.DateTimeProperty()
    last_blip = db.ReferenceProperty(Blip)
    cnt_following = db.IntegerProperty(default=0)
    cnt_follower = db.IntegerProperty(default=0)

    @classmethod
    def get_or_create_from_user(cls, user, notify=True):
        if isinstance(user, UserAuth):
            user = user.get_user()
        profile = ProfileByEmailView(user.email()).get()
        created = False
        if not profile:
            source = getattr(user, 'source', 'local')
            nickname = user.nickname()
            at_index = nickname.find('@')
            if at_index >= 0:
                nickname = nickname[:at_index]

            adder = 1
            orig_nick = nickname
            
            for p in Profile.all():
                logging.info(p.nickname)
            logging.info("profiles above")
            
            for i in xrange(1000):
                logging.info('finding nickname %s' % nickname)
                #if not Profile.gql('WHERE nickname=:1', nickname).get():
                if not ProfileByNickView(nickname).get():
                    logging.info('not found break')
                    break
                nickname = '%s_%s' % (orig_nick, adder)
                adder += 1

            profile = Profile(user_email=user.email(), nickname=nickname,
                              source=getattr(user, 'source', None),
                              fullname=nickname)
            created = True
            profile.put()

        if created and notify:
            p = ProfileByEmailView(settings.NEWS_USER).get()
            if p:
                Blip.new(p.get_user(), '@%s joined.' % profile.nickname)
        return created, profile

    def after_put(self):
        ProfileByEmailView(self.user_email).put()
        ProfileByNickView(self.nickname).put()
        
    def get_user(self):
        if self.source == 'google':
            _auth_domain = 'gmail.com'
        else:
            _auth_domain = auth_domain
        
        u = users.User(email=self.user_email,
                       _auth_domain=_auth_domain,
                       _user_id=None)
        u.source = self.source
        return u

    def set_avatar(self, data):
        if self.avatar:
            self.avatar.is_active = False
            self.avatar.put()
        self.avatar = AvatarImage.upload(data)
        
    def href(self):
        return '/u/%s' % self.nickname

    def href_key(self):
        return '/k/%s' % self.key()

    def avatar_href(self):
        if self.avatar:
            return self.avatar.href()
        else:
            return '/static/pics/default_avatar.png'

    def avatar_href_small(self):
        if self.avatar:
            return self.avatar.href_small()
        else:
            return '/static/pics/default_avatar_cc_60.png'

    def avatar_href_tiny(self):
        if self.avatar:
            return self.avatar.href_tiny()
        else:
            return '/static/pics/default_avatar_cc_32.png'
