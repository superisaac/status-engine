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

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from views.main_page import MainPage, PublicTimeline
from views.blip import BlipDeliverPage

url_mapping = [
    (r'/task/blip/deliver$', BlipDeliverPage),
    ]
app = webapp.WSGIApplication(url_mapping, debug=True)

def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()
