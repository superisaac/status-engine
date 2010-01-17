###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import urlparse
import logging
from helpers import HandlerBase, require_login, each_profiles
from models.article import Article, ArticleRevision
from models.profile import ProfileByNickView
from models.blip import Blip

class RevisionAddPage(HandlerBase):
    @require_login
    def get(self, article_key=None, errors=None):
        article = Article.get(article_key)
        if article is None or not article.is_active:
            return self.error(404)
        base_rev_key = self.request.get('base')
        base_rev = None
        if base_rev_key:
            base_rev = ArticleRevision.get(base_rev_key)
        if base_rev is None:
            base_rev = article.get_current_revision()
        content = base_rev.content
        return self.render('revision_add.html', locals())

    @require_login
    def post(self, article_key=None):
        article = Article.get(article_key)
        if article is None or not article.is_active:
            return self.error(404)

        errors = []
        content = self.request.get('content', '').strip()
        if not content:
            errors.append('Content cannot be empty')

        if errors:
            return self.render('revision_add.html', locals())

        user = self.get_current_user()
        rev = ArticleRevision(user=user, article=article,
                              content=content)
        rev.put()
        if user == article.creator:
            article.current_rev_key = str(rev.key())
        article.put()
        full_rev_url = urlparse.urljoin(self.request.uri, rev.href())
        blip = Blip.new(user, u'edited article %s %s' % (article.title,
                                                         full_rev_url))
        return self.redirect(article.href())
    
class ArticleAddPage(HandlerBase):
    @require_login
    def get(self, errors=None):
        return self.render('article_add.html', locals())

    @require_login
    def post(self):
        errors = []
        title = self.request.get('title', '').strip()
        if not title:
            errors.append('Title cannot be empty')

        content = self.request.get('content', '').strip()
        if not content:
            errors.append('Content cannot be empty')

        if errors:
            return self.render('article_add.html', locals())

        user = self.get_current_user()
        article = Article.new(user, title, content)
        full_article_url = urlparse.urljoin(self.request.uri, article.href())
        blip = Blip.new(user, u'added article %s %s' % (article.title,
                                                        full_article_url))

        return self.redirect(article.href())

class ArticleViewPage(HandlerBase):
    def get(self, article_key=None):
        article = Article.get(article_key)
        if article is None or not article.is_active:
            return self.error(404)

        revision = None
        rev_key = self.request.get('rev', '')
        if rev_key:
            revision = ArticleRevision.get(rev_key)

        if not revision:
            revision = article.get_current_revision()

        return self.render('article_view.html', locals())

class ArticleSetRevisionPage(HandlerBase):
    def post(self, article_key=None):
        article = Article.get(article_key)
        if article is None or not article.is_active:
            return self.error(404)
        rev_key = self.request.get('revision_key')
        if not rev_key:
            return self.error(404)
        rev = ArticleRevision.get(rev_key)
        if rev is None or rev.article.key() != article.key():
            return self.error(401)
        article.current_rev_key = str(rev.key())
        article.put()
        return self.redirect(article.href())

class RevisionListPage(HandlerBase):
    def get(self, article_key=None):
        article = Article.get(article_key)
        if article is None or not article.is_active:
            return self.error(404)
        creator_view = self.get_current_user() == article.creator
        qs = article.revision_set
        qs.order('-date_created')
        revisions = each_profiles(qs)
        return self.render('revision_list.html', locals())

class ArticleListPage(HandlerBase):
    def get(self):
        article_qs = Article.all()
        nickname = self.request.get('user')
        if nickname:
            p= ProfileByNickView(nickname).get()
            if p:
                article_qs.filter('creator =', p.get_user())
        article_qs.order('-date_modified')
        articles = each_profiles(article_qs, field='creator')
        return self.render('article_list.html', locals())
