###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import sys, os
import logging
from helpers import HandlerBase, create_user
from google.appengine.ext import db
from models.migration import Migration
from models.profile import Profile
from models.blip import Blip, BlipLink
import settings

class MigrationTask(object):
    name = None
    def call(self, out):
        pass

class NewsUserTask(MigrationTask):
    name = 'news'
    def call(self, out):
        if Profile.gql('WHERE user_email = :1', settings.NEWS_USER).get():
            out.write('News user already exist')
            return
        news = create_user(settings.NEWS_USER,
                           settings.NEWS_PASSWORD).get_user()
class UpdateBlipLink(MigrationTask):
    name = 'update_bliplink'
    def call(self, out):
        for bliplink in BlipLink.all():
            blip = bliplink.blip
            bliplink.text = blip.text
            bliplink.date_blip_created = blip.date_created
            bliplink.author = blip.user
            bliplink.meeting = blip.meeting
            bliplink.attachment = blip.attachment
            bliplink.put()

tasklist = [NewsUserTask, UpdateBlipLink, UpdateBlipLink]

def migration_task(task):
    task.call(out)
    m = Migration(name=task.name)
    m.put()

class MigrationPage(HandlerBase):
    def get(self):
        cnt = 0
        for taskcls in tasklist:
            task = taskcls()
            t = Migration.all().filter('name =', task.name).get()
            if t is None:
                task.call(self.response.out)
                m = Migration(name=task.name)
                m.put()
                self.response.out.write('Performed task: %s.<br/>' % task.name)
                cnt += 1
            else:
                logging.info('Task %s already performed' % task.name)
        self.response.out.write('%s tasks have been executed<br/>' % cnt)
