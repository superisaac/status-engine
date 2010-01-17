###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import logging
import datetime
from google.appengine.api import users
from google.appengine.ext import db
from helpers import HandlerBase, require_login, each_profiles
from helpers import SimplePaginator
from models.profile import Profile, ProfileByNickView
from models.follow import Follow
from models.blip import Blip, BlipLink

class FollowPage(HandlerBase):
    @require_login
    def get(self, user_name=None):
        login_user = self.get_current_user()
        target_profile = ProfileByNickView(user_name).get()
        if target_profile is None:
            return self.error(404)
        target_user = target_profile.get_user()
        follow = Follow.new(login_user, target_user)
        if follow is None:
            return self.error(404)
        follow.update_profile()
        return self.redirect('/home')

class UnFollowPage(HandlerBase):
    @require_login
    def get(self, user_name=None):
        login_user = self.get_current_user()
        target_profile = ProfileByNickView(user_name).get()
        if target_profile is None:
            return self.error(404)
        target_user = target_profile.get_user()
        follow = Follow.gql("WHERE from_user=:1 AND to_user=:2", login_user, target_user).get()
        if follow:
            follow.delete()
            follow.update_profile()
        BlipLink.delete_for_author(login_user, target_user)
        return self.redirect('/home')
