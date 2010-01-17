###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import logging
from datetime import datetime
from google.appengine.ext import db
from mixins import CommonMixin

class Follow(CommonMixin, db.Model):
    from_user = db.UserProperty()
    to_user = db.UserProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def who_subscribe_you(cls, user, ancestor_key=None):
        params = {'to_user': user}
        if ancestor_key:
            an_stmt = 'and ancestor is :ancestor_key'
            params['ancestor_key'] = ancestor_key
        else:
            on_stmt = ''
            
        q = cls.gql("""
        where to_user = :to_user
        %s
        order by date_created desc
        """ % on_stmt, **params)
        return q

    @classmethod
    def your_subscribers(cls, user, ancestor_key=None):
        params = {'from_user': user}
        if ancestor_key:
            an_stmt = 'and ancestor is :ancestor_key'
            params['ancestor_key'] = ancestor_key
        else:
            on_stmt = ''
            
        q = cls.gql("""
        where from_user = :from_user
        %s
        order by date_created desc
        """ % on_stmt, **params)
        return q

    @classmethod
    def new(cls, from_user, to_user):
        from models.blip import Blip
        follow = cls.gql('WHERE from_user = :1 AND to_user = :2',
                         from_user, to_user).get()
        if follow:
            return None
        follow = cls(from_user=from_user,
                     to_user=to_user)
        follow.date_created = datetime.now()
        follow.put()
        Blip.deliver_legacy_to_user(to_user, from_user)
        return follow

    def update_profile(self):
        from models.profile import Profile
        _, from_profile = Profile.get_or_create_from_user(self.from_user)
        _, to_profile = Profile.get_or_create_from_user(self.to_user)

        q = Follow.gql('WHERE from_user = :1', self.from_user)
        from_profile.cnt_following = q.count()
        from_profile.put()

        q = Follow.gql('WHERE to_user = :1', self.to_user)
        to_profile.cnt_follower = q.count()
        to_profile.put()

