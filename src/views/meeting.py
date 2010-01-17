###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import sys, os
from models.meeting import Meeting, MeetingMember, UserMeetingListView
from models.profile import Profile
from models.follow import Follow
from models.blip import Blip, BlipLink
from helpers import HandlerBase, require_login
from helpers import SimplePaginator, each_profiles
import settings

class MeetingListPage(HandlerBase):
    @require_login
    def get(self):
        login_user = self.get_current_user()
        meetings = UserMeetingListView(login_user).get()
        return self.render('meeting_list.html', locals())

class MeetingAddPage(HandlerBase):
    @require_login
    def get(self):
        " Create a new meeting. "
        login_user = self.get_current_user()
        m = Meeting(creator=login_user)
        m.put()
        return self.redirect(m.href())

class MeetingViewPage(HandlerBase):
    @require_login
    def get(self, meeting_key=None):
        from models.blip import Blip
        login_user = self.get_current_user()
        meeting = Meeting.get(meeting_key)
        if meeting is None or not meeting.is_active:
            return self.error(404)
        if not meeting.has_member(login_user):
            return self.error(401)
        c, p = Profile.get_or_create_from_user(meeting.creator)
        
        admin_profiles = [p]

        member_profiles = []
        members = meeting.members(include_creator=False)
        for u in members:
            c, p = Profile.get_or_create_from_user(u)
            member_profiles.append(p)

        followees = Follow.your_subscribers(login_user)
        followee_profiles = []
        for f in followees:
            if f.to_user not in members:
                c, p = Profile.get_or_create_from_user(f.to_user)
                followee_profiles.append(p)
            
        try:
            page = int(self.request.get('page', '1'))
        except ValueError:
            page = 1

        pagesize = settings.ROOM_PAGE_SIZE
        paginator = SimplePaginator(Blip.qs_for_meeting(meeting),
                                     page, pagesize)
        
        blips = each_profiles(paginator.object_list)
        return self.render('meeting_item.html', locals())

class MeetingDeletePage(HandlerBase):
    @require_login
    def get(self, meeting_key=None):
        login_user = self.get_current_user()
        m = Meeting.get(meeting_key)
        if m is None:
            return self.error(404)
        if m.creator != login_user:
            return self.error(401) # access denied
        m.delete()
        return self.redirect_back()

class MeetingAddMemberPage(HandlerBase):
    @require_login
    def post(self, meeting_key=None):
        login_user = self.get_current_user()
        m = Meeting.get(meeting_key)
        if m is None:
            return self.error(404)
        if m.creator != login_user:
            return self.error(401)
        
        user_name = self.request.get('user_name')
        profile = Profile.gql('WHERE nickname = :1', user_name).get()
        if profile:
            m.add_member(profile.get_user())
        return self.redirect_back()

class MeetingDeleteMemberPage(HandlerBase):
    @require_login
    def get(self, meeting_key=None, user_name=None):
        login_user = self.get_current_user()
        m = Meeting.get(meeting_key)
        if m is None:
            return self.error(404)
        if m.creator != login_user:
            return self.error(401)

        profile = Profile.gql('WHERE nickname = :1', user_name).get()
        m.delete_member(profile.get_user())
        return self.redirect_back()

class MeetingUpdatePage(HandlerBase):
    @require_login
    def post(self, meeting_key=None):
        from models.blip import Blip
        login_user = self.get_current_user()
        m = Meeting.get(meeting_key)
        if m is None:
            return self.error(404)
        if not m.has_member(login_user):
            return self.error(401)

        content = self.request.get('text', '').strip()
        attachment = self.request.get('attachment', '').strip()
        blip = Blip.new(login_user, content,
                        attachment=attachment, meeting=m)
        return self.redirect(m.href())

class MeetingBlipDeletePage(HandlerBase):
    @require_login
    def get(self, blip_key=None):
        login_user = self.get_current_user()
        blip = Blip.get(blip_key)
        if blip is None:
            return self.error(404)
        if blip.user != login_user:
            return self.error(401)

        m = blip.meeting
        if m is None:
            return self.error(404)
        
        q = BlipLink.gql('WHERE blip = :1', blip)
        for link in q:
            link.delete()

        blip.delete()
        return self.redirect_back()
