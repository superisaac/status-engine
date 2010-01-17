###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

from google.appengine.dist import use_library
use_library('django', '1.1')

import settings

import cache_layer
cache_layer.install()

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from views.main_page import MainPage, PublicTimeline
from views.auth import LoginPage, LogoutPage, SignupPage
from views.profile import ProfileEditPage, UserPage, HomePage
from views.follow import FollowPage, UnFollowPage
from views.blip import BlipPostPage, BlipLinkDeletePage, BlipViewPage, BlipLinkViewPage
from views.misc import ImagePage
from views.meeting import MeetingAddPage, MeetingListPage, MeetingViewPage
from views.meeting import MeetingUpdatePage, MeetingAddMemberPage
from views.meeting import MeetingDeleteMemberPage, MeetingBlipDeletePage
from views.map import MapView, MapEditView

from views.article import RevisionAddPage, ArticleAddPage, ArticleViewPage
from views.article import RevisionListPage, ArticleListPage, ArticleSetRevisionPage

url_mapping = [
    ('/signin', LoginPage),
    ('/signout', LogoutPage),
    (r'/signup', SignupPage),
    ('/profile/edit', ProfileEditPage),
    ('/home', HomePage),
    (r'/u/(?P<user_name>[\.\-\w]+)/unfollow$', UnFollowPage),
    (r'/u/(?P<user_name>[\.\-\w]+)/follow$', FollowPage),
    (r'/u/(?P<user_name>[\.\-\w]+)$', UserPage),
    (r'/blip/update$', BlipPostPage),
    (r'/blip/(?P<blip_link_key>[^/]+)/delete$', BlipLinkDeletePage),
    (r'/blip/(?P<blip_key>[^/]+)$', BlipViewPage),
    (r'/bliplink/(?P<blip_link_key>[^/]+)$', BlipLinkViewPage),

    (r'/meeting/add', MeetingAddPage),
     (r'/meeting/blip/(?P<blip_key>\w+)/delete$', MeetingBlipDeletePage),
    (r'/meeting/(?P<meeting_key>\w+)/member/add$',
     MeetingAddMemberPage),
    (r'/meeting/(?P<meeting_key>\w+)/(?P<user_name>[\.\-\w]+)/delete$',
     MeetingDeleteMemberPage),


    (r'/meeting/(?P<meeting_key>\w+)/update$', MeetingUpdatePage),
    (r'/meeting/(?P<meeting_key>\w+)$', MeetingViewPage),
    (r'/meeting/', MeetingListPage),
    (r'/image/(?P<image_key>.+)\.png', ImagePage),

    (r'/map/edit$', MapEditView),
    (r'/map$', MapView),
    (r'/public$', PublicTimeline),

    (r'/article/add', ArticleAddPage),
    (r'/article/(?P<article_key>\w+)/rev/add$', RevisionAddPage),
    (r'/article/(?P<article_key>\w+)/rev/set$', ArticleSetRevisionPage),
    (r'/article/(?P<article_key>\w+)/rev/$', RevisionListPage),

    (r'/article/(?P<article_key>\w+)', ArticleViewPage),
    (r'/article/$', ArticleListPage),    
    
    ('/', MainPage),
    ]
app = webapp.WSGIApplication(url_mapping, debug=True)

def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()
