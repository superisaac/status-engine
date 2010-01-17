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
from models.profile import Profile, UserAuth

from models.follow import Follow
from models.blip import Blip, BlipLink
import settings

class ProfileEditPage(HandlerBase):
    errors = []
    @require_login
    def get(self):
        user = self.get_current_user()
        created, profile = Profile.get_or_create_from_user(user)
        errors = self.errors
        return self.render('profile_edit.html', locals())

    def validate(self, profile):
        nickname = self.request.get('nickname', '').strip()
        if nickname:
            if Profile.gql('WHERE nickname=:1 AND __key__ != :2',
                           nickname,
                           profile.key()).get():
                raise Exception('Nickname already been taken')
        else:
            raise Exception('Nickname cannot be empty')

        fullname = self.request.get('fullname', '').strip()
        if not fullname:
            raise Exception('Full name cannot be empty')

    @require_login
    def post(self):
        user = self.get_current_user()
        created, profile = Profile.get_or_create_from_user(user)
        self.errors = []
        try:
            self.validate(profile)
        except Exception, e:
            self.errors = [str(e)]
            return self.get()
            
        nickname = self.request.get('nickname')
        avatar = self.request.get('avatar')
        fullname = self.request.get('fullname')
        profile.fullname = fullname
        try:
            if avatar:
                profile.set_avatar(avatar)
            if nickname:
                profile.nickname = nickname
            profile.has_edited = True
            profile.put()
        except Exception, e:
            self.errors.append(str(e))
            return self.get()
        return self.redirect('/')

class UserPage(HandlerBase):
    def get(self, user_name=None):
        login_user = self.get_current_user()

        if user_name is None:
            return self.redirect('/signin')

        profile = Profile.gql('WHERE nickname=:1', user_name).get()
        if not profile or not profile.is_active:
            return self.error(404)
        user = profile.get_user()
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

        try:
            page = int(self.request.get('page', '1'))
        except ValueError:
            page = 1

        has_followed = Follow.gql('WHERE from_user = :1 AND to_user =:2',
                                  login_user,
                                  user).get()
        pagesize = settings.BLIP_PAGE_SIZE
        paginator = SimplePaginator(Blip.qs_for_author(user),
                                    page, pagesize)

        blips = each_profiles(paginator.object_list)
        return self.render('user_page.html', locals())

class HomePage(HandlerBase):
    @require_login
    def get(self):
        user = self.get_current_user()
        created, profile = Profile.get_or_create_from_user(user)

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
        try:
            page = int(self.request.get('page', '1'))
        except ValueError:
            page = 1

        pagesize = settings.BLIP_PAGE_SIZE
        paginator = SimplePaginator(BlipLink.qs_for_user(user),
                                    page, pagesize)
        blips = each_profiles(paginator.object_list, field='author')
        is_self = True
        return self.render('home.html', locals())

class ResetPasswordPage(HandlerBase):
    def post(self):
        errors = []
        email = self.request.get('email', '')
        user_auth = None
        if not email:
            errors.append('Email cannot be empty')
        else:
            user_auth = UserAuth.gql('WHERE email = :1', email).get()
            if user_auth is None:
                errors.append('Local user of %s not found' % email)

        password = self.request.get('password', '')
        if not password:
            errors.append('Password is empty')
        password2 = self.request.get('password2', '')
        logging.info('%s: %s' % (password2, password))
        if password2 != password:
            errors.append('Password retyped wrong')
        if errors:
            return self.get(errors=errors)
        user_auth.set_password(password)
        self.response.out.write('Password reset ok.')

    def get(self, errors=None):
        return self.render('reset_password.html', locals())

        
