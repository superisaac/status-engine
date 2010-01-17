###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import logging
import datetime
from google.appengine.ext import db
from google.appengine.api import images
from mixins import CommonMixin

def crop_center(img, sz):
    ow, oh = img.width, img.height
    left, top = 0.0, 0.0
    bottom = 1.0
    right = 1.0
    if ow > oh:
        left = float((ow - oh) / 2) / ow
        right = 1.0 - left
    else:
        top = float((oh - ow) /  2) / oh
        bottom = 1.0 - top
    img.crop(left, top, right, bottom)
    img.resize(sz, sz)
    
class AvatarImage(CommonMixin, db.Model):
    data = db.BlobProperty()
    data_cc_32 = db.BlobProperty()
    data_cc_60 = db.BlobProperty()
    
    is_active = db.BooleanProperty(default=True)
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_modified = db.DateTimeProperty()

    def put(self):
        self.date_modified = datetime.datetime.now()
        return super(AvatarImage, self).put()
    
    @classmethod
    def upload(cls, odata):
        entr = cls()
        img = images.Image(odata)
        img.resize(width=256, height=256)
        entr.data = db.Blob(img.execute_transforms())

        crop_center(img, 60)
        entr.data_cc_60 = db.Blob(img.execute_transforms())

        crop_center(img, 32)
        entr.data_cc_32 = db.Blob(img.execute_transforms())

        entr.put()
        return entr

    def href(self):
        return '/image/%s.png' % self.key()

    def href_small(self):
        return '%s?sz=cc_60' % self.href()

    def href_tiny(self):
        return '%s?sz=cc_32' % self.href()

