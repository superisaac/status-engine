###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

import re
from models.image import AvatarImage
from datetime import datetime, timedelta
from helpers import HandlerBase, format_date

image_max_age = 24 * 3600 * 300;

class ImagePage(HandlerBase):
    def get(self, image_key=None):
        if not image_key:
            return self.error(404)
        image = AvatarImage.get(image_key)
        if not image:
            return self.error(404)
        
        sz = self.request.get('sz')
        if sz == 'cc_32':
            data = image.data_cc_32
        elif sz == 'cc_60':
            data = image.data_cc_60
        else:
            data = image.data

        if not data:
            return self.error(404)
        
        self.response.headers['Content-Type'] = 'image/png'
        self.response.headers['Cache-control'] = 'public, max-age=%s' % image_max_age
        self.response.headers['Expires'] = format_date(datetime.now() + timedelta(days=365))
        self.response.out.write(data)
