import re
import random, os, sys
import string
import urllib
from datetime import datetime
from urlparse import urlparse, ParseResult
#import simplejson
from HTMLParser import HTMLParser

def random_str(length=10):
    return ''.join(random.sample(string.ascii_letters, length))

def random_date_str(length=10):
    rs = random_str(length)
    return '%s-%s' % (datetime.now().strftime('%Y%m%d'),
                      rs)


def url_add_query(url, **kw):
    """
    In python2.6 urlparse parses a url into a ParseResult object while
    in prior version urlparse's result is a tuple of six elements.
    """
    u = urlparse(url)
    added_query = urllib.urlencode(kw)
    query = u.query
    if u.query:
        query = added_query + '&' + query
    else:
        query = added_query
    p = ParseResult(u.scheme, u.netloc, u.path,
                    u.params, query, u.fragment)
    return p.geturl()


class TextExtractor(HTMLParser):
    def __init__(self, sz_limit=100):
        HTMLParser.__init__(self)
        self.data = ''
        self.sz_limit = sz_limit
        self.skip = False
        
    def handle_starttag(self, tag, attrs):
        if tag.lower() in ('style', 'script'):
            self.skip = True

    def handle_endtag(self, tag):
        if tag.lower() in ('style', 'script'):
            self.skip = False

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        if self.skip:
            return
        #data = data.strip()
        data = data.replace(u'\u3000', ' ')
        data = re.sub(r'[\s\u3000][\s\u3000]+', ' ', data, re.U)
        self.data += data
        if len(self.data) > self.sz_limit:
            self.data = self.data[:self.sz_limit]
            raise DataOKException()

def extract_text(html_text, sz_limit=100, use_strip=True):
    parser = TextExtractor(sz_limit=sz_limit)
    try:
        parser.feed(html_text)
    except DataOKException:
        pass
    if use_strip:
        return parser.data.strip()
    else:
        return parser.data
