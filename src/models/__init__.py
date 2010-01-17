###########################################################################################
# Status-engine - publish status to your follower or in a meeting.
# Copyright (C) 2009-2010 Zeng Ke
# Licensed under to term of GNU Affero General Public License Version 3 or Later (the "AGPL")
# http://www.gnu.org/licenses/agpl-3.0.html
#
###########################################################################################

from blip import Blip, BlipLink
from article import Article, ArticleRevision
from meeting import Meeting
import cache_layer

cache_layer.register(Blip)
cache_layer.register(BlipLink)
cache_layer.register(Meeting)
cache_layer.register(Article)
cache_layer.register(ArticleRevision)

