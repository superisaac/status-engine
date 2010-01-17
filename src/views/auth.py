###########################################################################################
#
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import re
import logging
import datetime
from google.appengine.api import users
from google.appengine.ext import db
from helpers import HandlerBase, create_user, login_using_google, login_using_local
from models.profile import Profile, UserAuth

class LogoutPage(HandlerBase):
    def get(self):
        self.logout()
        return self.redirect('/signin')

class LoginPage(HandlerBase):
    def get(self):
        if not login_using_local():
            return self.error(404)
        continue_to = self.request.get('continue_to', '')
        google_login_url = users.create_login_url(continue_to)
        using_google = login_using_google()
        return self.render('signin.html', locals())

    def post(self):
        if not login_using_local():
            return self.error(404)
        email = self.request.get('email')
        password = self.request.get('password')
        continue_to = self.request.get('continue_to', '/')
        
        google_login_url = users.create_login_url(continue_to)
        errors = []
        local_user = UserAuth.gql('WHERE email=:1', email).get()
        if local_user and self.authenticate(local_user, password):
            login_user = local_user.get_user()
            profile = Profile.gql('WHERE user = :1', login_user).get()
            if not profile:
                created, profile = Profile.get_or_create_from_user(login_user)
                if created:
                    self.redirect('/profile/edit')
            return self.redirect(continue_to)
        else:
            errors.append('Login error, please relogin again')
        using_google = login_using_google()
        return self.render('signin.html', locals())

email_pattern = re.compile(r'[\w\.\-\+]+@[\w\-]+(\.[\w\-]+)+$', re.I)

class SignupPage(HandlerBase):
    def get(self):
        if not login_using_local():
            return self.error(404)
        return self.render('signup.html', locals())

    def validate(self, email, password):
        if not email_pattern.match(email):
            raise Exception("Email format is not right")

        if not password or not email:
            raise Exception("Password and email cannot be empty")

        profile = Profile.gql('WHERE user_email=:1', email).get()
        if profile:
            raise Exception("This email is already occupied.")

    def post(self):
        if not login_using_local():
            return self.error(404)
        email = self.request.get('email')
        password = self.request.get('password')
        errors = []
        try:
            self.validate(email, password)
            logging.info('validated')
            user = create_user(email, password)
            logging.info('created user')
            self.authenticate(user, password)
            logging.info('authed')
            return self.redirect('/profile/edit')
        except Exception, e:
            logging.error('Error %s' % e)
            errors.append(str(e))
        return self.render('signup.html', locals())
            
        
        
