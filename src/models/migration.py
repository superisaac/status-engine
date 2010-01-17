###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import logging
from datetime import datetime
from google.appengine.ext import db
from mixins import CommonMixin

class Migration(CommonMixin, db.Model):
    name = db.StringProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)

        
