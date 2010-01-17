###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import logging
from datetime import datetime
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from models.follow import Follow
from mixins import CommonMixin, CacheView
from models.meeting import Meeting
import settings

class PublicTimeView(CacheView):
    def load(self):
        qs = db.GqlQuery('''
        SELECT __key__ from Blip
        where meeting = :1
        order by date_created desc
        limit %s
        ''' % settings.BLIP_PAGE_SIZE , None)
        bliplist = []
        for blip_key in qs.fetch(settings.BLIP_PAGE_SIZE):
            blip = db.get(blip_key)
            bliplist.append(blip)
        return bliplist
    
    def get_key_name(self):
        return 'b:public_timeline'
    
class Blip(CommonMixin, db.Model):
    text = db.TextProperty()
    user = db.UserProperty()
    to_user = db.UserProperty()
    meeting = db.ReferenceProperty(Meeting)
    date_created = db.DateTimeProperty(auto_now_add=True)
    attachment = db.StringProperty()

    def href(self):
        return '/blip/%s' % self.key()

    def deliver_to_followers(self):
        subscribers = Follow.who_subscribe_you(self.user)
        users = set(f.from_user for f in subscribers)
        if self.to_user:
            to_subscribers = set(Follow.who_subscribe_you(self.to_user))
            users = users.intersection(set(f.from_user for f in
                                           to_subscribers))
            users.add(self.to_user)
        #users.add(self.user)
        self.deliver_to_users(users)

    def deliver(self):
        if self.meeting:
            self.deliver_in_meeting()
        else:
            self.deliver_to_followers()

    def deliver_to_users(self, users):
        logging.info('deliver to users %s' % users)
        for u in users:
            if u != self.user:
                logging.debug('delivered %s to %s' % (self.text, u))
                link = BlipLink.new(u, self)

    def deliver_in_meeting(self):
        users = self.meeting.members()
        self.deliver_to_users(users)

    @classmethod
    def deliver_legacy_to_user(cls, from_user, to_user, limit=100):
        qs = cls.all()
        qs.filter('user =', from_user)
        qs.filter('meeting =', None)
        qs.order('-date_created')
        rs = qs.fetch(limit)
        for blip in rs:
            blip.deliver_to_users([to_user])

    @classmethod
    def deliver_legacy_to_meeting_user(cls, meeting, to_user, limit=100):
        qs = cls.all()
        qs.filter('meeting =', meeting)
        qs.order('-date_created')
        rs = qs.fetch(limit)
        for blip in rs:
            blip.deliver_to_users([to_user])
    
    @classmethod
    def new(cls, user, content, attachment='', meeting=None):
        from helpers import  filter_blip
        from models.profile import Profile
        if content:
            content, user_names, urls = filter_blip(content)
            to_user = None
            if content.startswith('@'):
                profile = Profile.gql('WHERE nickname = :1', user_names[0]).get()
                if profile:
                    to_user = profile.get_user()
            blip = cls(text=content, user=user,
                       attachment=attachment, to_user=to_user,
                       meeting=meeting)
            blip.put()
            link = BlipLink.new(blip.user, blip)
            task = taskqueue.Task(url='/task/blip/deliver',
                                  params={'key': blip.key()})
            task.add(queue_name='status-delivery')
            return blip
            
        
    def get_date_repr(self, date_base=None):
        if date_base is None:
            date_base = self.date_created
        delta = datetime.now() - date_base
        from helpers import date_repr
        return date_repr(delta)

    @classmethod
    def qs_for_author(cls, author):
        qs = cls.all()
        qs.filter('user =', author)
        qs.filter('meeting =', None)
        qs.order('-date_created')
        return qs

    @classmethod
    def qs_for_meeting(cls, meeting, order='-date_created'):
        qs = cls.all()
        qs.filter('meeting =', meeting)
        qs.order(order)
        return qs

    @classmethod
    def qs_for_public(cls):
        qs = cls.all()
        qs.filter('meeting =', None)
        qs.order('-date_created')
        return qs

    def after_put(self):
        PublicTimeView().put()
        if self.meeting:
            self.meeting.put()
        
class BlipLink(CommonMixin, db.Model):
    text = db.TextProperty()
    user = db.UserProperty()
    author = db.UserProperty()
    blip = db.ReferenceProperty(Blip)
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_blip_created = db.DateTimeProperty(default=None)
    to_user = db.UserProperty()
    meeting = db.Reference(Meeting)
    attachment = db.StringProperty()

    @classmethod
    def new(cls, user, blip):
        bl = cls(text=blip.text, author=blip.user, user=user,
                 blip=blip, date_blip_created=blip.date_created,
                 meeting=blip.meeting, attachment=blip.attachment)
        bl.put()
        return bl
            
    def put(self):
        if self.date_blip_created is None:
            self.date_blip_created = self.blip.date_created
        return super(BlipLink, self).put()

    @classmethod
    def qs_for_user(cls, user):
        qs = cls.all()
        qs.filter('user =', user)
        qs.order('-date_blip_created')
        return qs

    @classmethod
    def delete_for_author(cls, user, author):
        for _ in xrange(200):
            q = cls.gql('WHERE user =:1 AND author = :2',
                        user, author)
            if q.count() <= 0:
                break
            results = q.fetch(900)
            db.delete(results)

    @classmethod
    def delete_for_blip(cls, blip):
        for _ in xrange(200):
            q = cls.gql('WHERE blip=:1', blip)
            if q.count() <= 0:
                break
            results = q.fetch(900)
            db.delete(results)

    def get_date_repr(self, date_base=None):
        if date_base is None:
            date_base = self.date_blip_created
        delta = datetime.now() - date_base
        from helpers import date_repr
        return date_repr(delta)

    def href(self):
        return '/bliplink/%s' % self.key()

