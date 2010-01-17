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
from helpers import HandlerBase, require_login
from helpers import attachment_to_html
from models.follow import Follow
from models.blip import Blip, BlipLink
from models.profile import Profile

class BlipPostPage(HandlerBase):
    @require_login        
    def post(self):
        content = self.request.get('text', '').strip()
        attachment = self.request.get('attachment', '').strip()
        blip = Blip.new(self.get_current_user(), content, attachment)
        return self.redirect('/home')

class BlipLinkDeletePage(HandlerBase):
    @require_login
    def get(self, blip_link_key=None):
        login_user = self.get_current_user()
        bliplink = BlipLink.get(blip_link_key)
        if bliplink is None:
            return self.redirect_back()

        if login_user == bliplink.author:
            logging.debug('delete all blip')
            blip = bliplink.blip
            BlipLink.delete_for_blip(blip)
            blip.delete()
        else:
            logging.debug('delete only the blip link')
            bliplink.delete()
        return self.redirect_back()

class BlipLinkViewPage(HandlerBase):
    def get(self, blip_link_key=None):
        bliplink = BlipLink.get(blip_link_key)
        return self.redirect(bliplink.blip.href())

class BlipViewPage(HandlerBase):
    def get(self, blip_key=None):
        blip = Blip.get(blip_key)
        if blip is None:
            return self.error(404)
        login_user = self.get_current_user()
        if blip.meeting and not blip.meeting.has_member(login_user):
            return self.error(401)
        user = blip.user
        _, profile = Profile.get_or_create_from_user(user)

        is_self = user == login_user

        has_followed = False
        if not is_self:
            has_followed = Follow.gql('WHERE from_user = :1 AND to_user = :2',
                                      login_user, user).get() is not None            

        followers = Follow.who_subscribe_you(user)
        follower_profiles = []
        for f in followers:
            c, p = Profile.get_or_create_from_user(f.from_user)
            follower_profiles.append(p)
        followees = Follow.your_subscribers(user)
        followee_profiles = []
        for f in followees:
            c, p = Profile.get_or_create_from_user(f.to_user)
            followee_profiles.append(p)


        return self.render('blip_item.html', locals())

class BlipDeliverPage(HandlerBase):
    def post(self):
        logging.debug('delivering jokes')
        blip_key = self.request.get('key')
        if blip_key:
            blip = Blip.get(blip_key)
            blip.deliver()
        else:
            logging.error('blip key must be provided')
