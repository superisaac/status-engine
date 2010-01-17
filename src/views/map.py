###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import logging
import datetime
from helpers import HandlerBase
from google.appengine.api import users
from google.appengine.ext import db
import settings

class MapView(HandlerBase):
    def get(self):
        lat = self.request.get('lat', '37.4419')
        lng = self.request.get('lng', '-122.1419')
        width = self.request.get('width', 360)
        height = self.request.get('height', 360)
        description = self.request.get('description', '')
        zoom_level = self.request.get('zoom_level', '13')
        map_key = settings.MAP_KEY
        size_style = 'width:%spx; height:%spx;' % (width, height)
        big = False
        return self.render('map/index.html', locals())

class MapEditView(HandlerBase):
    def get(self):
        lat = self.request.get('lat', '37.4419')
        lng = self.request.get('lng', '-122.1419')
        description = self.request.get('description', 'AAA')
        zoom_level = self.request.get('zoom_level', '13')
        map_key = settings.MAP_KEY
        return self.render('map/edit.html', locals())

