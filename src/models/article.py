###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import os, sys
from datetime import datetime
from google.appengine.ext import db
from mixins import CommonMixin
from utils import extract_text

class Article(CommonMixin, db.Model):
    creator = db.UserProperty()
    is_active = db.BooleanProperty(default=True)
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_modified = db.DateTimeProperty(auto_now_add=True)
    title = db.StringProperty()
    current_rev_key = db.StringProperty(default='')

    def get_current_revision(self):
        return ArticleRevision.get(self.current_rev_key)

    @classmethod
    def new(cls, user, title, content):
        article = cls(creator=user, title=title)
        article.put()
        rev = ArticleRevision(article=article,
                              user=user,
                              content=content)
        rev.put()
        article.current_rev_key = str(rev.key())
        article.put()
        return article

    def href(self):
        return '/article/%s' % self.key()

    def get_date_repr(self, date_base=None):
        if date_base is None:
            date_base = self.date_created
        delta = datetime.now() - date_base
        from helpers import date_repr
        return date_repr(delta)

    def get_modified_date_repr(self):
        date_base = self.date_modified
        delta = datetime.now() - date_base
        from helpers import date_repr
        return date_repr(delta)

class ArticleRevision(CommonMixin, db.Model):
    date_created = db.DateTimeProperty(auto_now_add=True)
    user = db.UserProperty()
    content = db.TextProperty(default='')
    abstract = db.TextProperty(default='')
    article = db.ReferenceProperty(Article, collection_name='revision_set')

    def href(self):
        return '/article/%s?rev=%s' % (self.article.key(), self.key())

    def get_abstract(self):
        return self.abstract or '-- No text --'

    def before_put(self):
        self.abstract = extract_text(self.content, sz_limit=200)
        
            

