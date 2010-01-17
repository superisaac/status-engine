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
from helpers import HandlerBase, create_user, each_profiles
from models.profile import Profile
from models.follow import Follow
from models.blip import Blip, BlipLink, PublicTimeView
import settings

class InitData(HandlerBase):
    def get(self):
        if Profile.gql('WHERE user_email = :1', settings.NEWS_USER).get():
            self.response.out.write('Already exist')
            return
        news = create_user(settings.NEWS_USER, 'halihalinews').get_user()

        #user = create_user('kaka@abc.com', '1111').get_user()
        #person = create_user('person@abc.com', '1111').get_user()
        #grade = create_user('grade@abc.com', '1111').get_user()

        #for i in range(1, 21):
        #    ut = create_user('user_%s@abc.com' % i, '1111').get_user()
        #    Follow.new(ut, user)
        #    Follow.new(person, ut)
        #Follow.new(user, person)
        #Follow.new(person, grade)
        
        self.response.out.write('OK')

class BuildBlipLink(HandlerBase):
    def get(self):
        cnt = 0
        for bl in BlipLink.all():
            bl.date_blip_created = bl.blip.date_created
            bl.put()
            cnt += 1
        self.response.out.write('build %s blip links' % cnt)

class PublicTimeline(HandlerBase):
    def get(self):
        pagesize = settings.BLIP_PAGE_SIZE
        #qs = Blip.qs_for_public()
        view = PublicTimeView()
        #results = qs.fetch(pagesize)
        blips = each_profiles(view.get())
        return self.render('public.html', locals())

        
class MainPage(HandlerBase):
    def get(self):
        user = self.get_current_user()
        link = users.create_login_url(self.request.uri)
        if user:
            return self.redirect('/home')
        else:
            return self.redirect('/public')
