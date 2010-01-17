###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import logging
from mixins import CommonMixin, CacheView
from google.appengine.ext import db

class MeetingSnapView(CacheView):
    def __init__(self, meeting):
        self.meeting = meeting

    def get_key_name(self):
        return 'msnap:%s' % self.meeting.key()

    def load(self):
        from models.blip import Blip
        q = Blip.qs_for_meeting(self.meeting, order='date_created')
        text = ' '.join(blip.text for blip in q.fetch(3))
        return text

class MeetingMembersView(CacheView):
    def __init__(self, meeting):
        self.meeting = meeting

    def get_key_name(self):
        return 'mmember:%s' % self.meeting.key()

    def load(self):
        users = set()
        for mm in MeetingMember.gql('WHERE meeting = :1',
                                    self.meeting).fetch(100):
            u = mm.user
            users.add(u) 
        return users

class UserMeetingListView(CacheView):
    def __init__(self, user):
        self.user = user

    def get_key_name(self):
        return 'um:%s' % self.user.email()

    def load(self):
        q = MeetingMember.gql('WHERE user = :1', self.user)
        meetings = set(mm.meeting for mm in q.fetch(100))
        q = Meeting.gql('WHERE creator = :1', self.user)
        meetings.update(set(q.fetch(100)))
        omeetings = set()
        for m in meetings:
            if m.is_active:
                omeetings.add(m)
        return omeetings
        
class Meeting(CommonMixin, db.Model):
    creator = db.UserProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_modified = db.DateTimeProperty(auto_now_add=True)
    is_active = db.BooleanProperty(default=True)

    def blip_text(self):
        return MeetingSnapView(self).get()

    def after_put(self):
        MeetingSnapView(self).put()
        MeetingMembersView(self).put()
        UserMeetingListView(self.creator).put()
        
    def members(self, include_creator=True):
        users = MeetingMembersView(self).get()
        if include_creator:
            users.add(self.creator)
        return users

    def member_profiles(self, include_creator=True):
        from models.profile import Profile
        for _, user in zip(xrange(4), self.members(include_creator)):
            _, p = Profile.get_or_create_from_user(user)
            yield p

    def delete_member(self, user):
        from models.blip import Blip, BlipLink

        mm = MeetingMember.gql('WHERE meeting = :1 AND user =:2',
                               self, user).get()
        if mm:
            mm.delete()
            for blip in Blip.gql('WHERE meeting = :1 AND user != :2', self, user):
                #bl = BlipLink.gql('WHERE blip = :1', blip).get()
                bl_key = db.GqlQuery('select __key__ from BlipLink WHERE blip = :1', blip).get()
                logging.info('bl key %s' % bl_key)
                if bl_key:
                    #bl.delete()
                    db.delete(bl_key)
            self.put()
        else:
            logging.warn("User %s is not found in meeting %s to delete" %
                         (user, self))

    def add_member(self, user):
        from models.blip import Blip
        if MeetingMember.gql('WHERE meeting = :1 AND user =:2',
                          self, user).get():
            logging.warn("Already added user %s to meeting %s" %
                         (user, self.key()))
            return
        mm = MeetingMember(meeting=self, user=user)
        mm.put()
        Blip.deliver_legacy_to_meeting_user(self, user)
        self.put()

    def href(self):
        return '/meeting/%s' % self.key()

    def has_member(self, user):
        if user == self.creator:
            return True
        return MeetingMember.gql('WHERE meeting = :1 AND user = :2',
                                 self, user).get() is not None

class MeetingMember(CommonMixin, db.Model):
    meeting = db.ReferenceProperty(Meeting)
    user = db.UserProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)

    def after_put(self):
        self.meeting.put()

