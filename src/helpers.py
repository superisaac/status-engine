import re
import os
import logging
from time import mktime
import email.utils
import urllib
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import users
from models.profile import UserAuth, Profile
from models.blip import Blip
from models.profile import ProfileByEmailView

import settings
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

def login_using_google():
    return settings.LOGIN_METHOD in ('google', 'both')

def login_using_local():
    return settings.LOGIN_METHOD  in ('local', 'both')

def create_user(email, password):
    local_user = UserAuth.new(email)
    local_user.set_password(password)
    local_user.put()
    created, profile = Profile.get_or_create_from_user(local_user)
    return local_user
    
def render_template(response, template_file, values):
    path = os.path.join(template_dir, template_file)
    data = template.render(path, values)
    return response.out.write(data)


class HandlerBase(webapp.RequestHandler):
    auth_user = None
    error_msg = {
        400: 'Application error',
        404: 'Not Found',
        401: 'Access denied',
        405: 'Method not allowed'
        }
    def get_login_url(self):
        login_method = settings.LOGIN_METHOD
        if login_method == 'both':
            if self.is_google_account():
                return users.create_login_url('/')
            return '/signin'
        elif login_method == 'google':
            return users.create_login_url('/')
        else:
            assert login_method == 'local'
            return '/signin'

    def error(self, code):
        super(HandlerBase, self).error(code)
        if code >= 400 and code < 500:
            word = self.error_msg.get(code, 'Error status: %s' % code)
            self.response.out.write(word)


    def get_logout_url(self):
        if self.is_google_account():
            return users.create_logout_url('/')
        return '/signout'

    def _get_current_user_google(self):
        u = users.get_current_user()
        if u:
            u.source = 'google'
        return u

    def _get_current_user_local(self):
        session_key = self.request.cookies.get('SESSION')
        if session_key:
            local_user = UserAuth.get_by_session(session_key)
            if local_user:
                u = local_user.get_user()
                u.source = 'local'
                u.session_key = session_key
                return u
            
    def get_current_user(self):
        if self.auth_user:
            return self.auth_user

        login_method = settings.LOGIN_METHOD
        if login_method == 'both':
            self.auth_user = self._get_current_user_google()
            if self.auth_user is None:
                self.auth_user = self._get_current_user_local()
        elif login_method == 'google':
            self.auth_user = self._get_current_user_google()
        else:
            assert login_method == 'local'
            self.auth_user = self._get_current_user_local()

        if self.auth_user:

            p = ProfileByEmailView(self.auth_user.email()).get()
            if p and not p.is_active:
                self.auth_user = None
        return self.auth_user

    def is_google_account(self):
        return getattr(self.auth_user, 'source') == 'google'

    def is_local_user(self):
        return getattr(self.auth_user, 'source') == 'local'

    def set_cookie(self, name, value, path='/', expires=None):
        cookie_str = '%s=%s;' % (name, urllib.quote(str(value)))
        if expires:
            cookie_str += ' expires=%s;' % format_data(expires)
        cookie_str += ' path=%s;' % path
        self.response.headers['Set-Cookie'] = cookie_str

    def authenticate(self, user, password):
        logging.debug("checking password %s %s" % (user.email, password))
        if user.check_password(password):
            self.set_cookie('AUTH_USER', user.key())
            self.set_cookie('SESSION', user.session_key)
            return user

    def logout(self):
        #self.response.headers['Set-Cookie'] = 'AUTH_USER=; path=/;'
        self.set_cookie('AUTH_USER', '')
        self.set_cookie('SESSION', '')

    def keep_session(self):
        user = self.auth_user
        if user and getattr(user, 'source', None) == 'local':
            self.set_cookie('SESSION', getattr(user, 'session_key', ''))
        
    def render(self, template_file, values,
               content_type='text/html; charset=utf-8;'):
        self.response.headers['Content-Type'] = content_type
        values.update({'handler': self, 'settings': settings})
        self.keep_session()
        return render_template(self.response, template_file, values)

    def redirect(self, url):
        self.keep_session()
        return super(HandlerBase, self).redirect(url)

    def error(self, *args):
        self.keep_session()
        return super(HandlerBase, self).error(*args)

    def redirect_back(self, alt_url='/'):
        referer = os.getenv('HTTP_REFERER', alt_url)
        self.keep_session()
        return self.redirect(referer)

def require_login(func):
    def _check_user(self, *args, **kw):
        user = self.get_current_user()
        if user is None:
            if self.request.method == 'GET':
                params = urllib.urlencode({'continue_to': self.request.uri})
                return self.redirect('/signin?%s' % params)
            else:
                return self.redirect('/signin')
        return func(self, *args, **kw)
    return _check_user

def format_date(dtobj):
    """ Format date according RFC 1123
    """
    t = mktime(dtobj.timetuple())
    return email.utils.formatdate(t, localtime=False, usegmt=True)    

def each_profiles(qs, field='user', callback=None):
    for q in qs:
        c, p = Profile.get_or_create_from_user(getattr(q,
                                                       field))
        p.q = q
        if callback:
            name, value = callback(q)
            setattr(p, name, value)
        yield p
    

class SimplePaginator:
    def __init__(self, qs, page, pagesize):
        self.pagesize = pagesize
        self.qs = qs
        self.page = page
        self._has_prev = self.page > 1
        self._has_next = False
        self._get_object_list()
        
    def has_next(self):
        return self._has_next

    def next_page(self):
        return self._has_next and (self.page + 1) or self.page

    def has_prev(self):
        return self._has_prev

    def prev_page(self):
        return self._has_prev and (self.page - 1) or self.page
        
    def _get_object_list(self):
        objs = list(self.qs.fetch(self.pagesize + 1,
                                  (self.page - 1) * self.pagesize))
        self._has_next = len(objs) > self.pagesize
        self.object_list = objs[:self.pagesize]
        
url_pattern = re.compile(r'(\b(https|http|feed)://[\-\w]+(\.[\-\w]+)*(:\d+)?(/[\S]*)?)', re.I)
user_pattern = re.compile(r'@(?P<uname>[a-z][\.\-\w]*)', re.I)

def limit_string(url, limit=20):
    if len(url) > limit:
        return url[:limit - 3] + '...'
    else:
        return url
    
def filter_blip(blip):
    user_names = []
    def sub_user(m):
        user_name = m.group('uname')
        user_names.append(user_name)
        return u'@<a href="/u/%s">%s</a>' % (user_name, user_name)
    blip = user_pattern.sub(sub_user, blip)
    
    urls = []
    def sub_url(m):
        url = m.group(1)
        urls.append(url)
        return u'<a href="%s">%s</a>' % (url,
                                         limit_string(url, 35))
    blip = url_pattern.sub(sub_url, blip)
    return blip, user_names, urls

def attachment_to_html(attachment):
    attachs = attachment.split()
    s = ''
    for attach in attachs:
        tp, url = attach.split('=', 1)
        if tp == 'img':
            s += """
            <img src="%s"></img>
            """ % (url,)
    return s
    
def date_repr(delta):
    if delta.days >= 365:
        return 'years ago'
    elif delta.days > 1:
        return '%s days ago' % delta.days
    elif delta.days == 1:
        return '1 day ago'
    elif delta.seconds > 3600:
        return '%s hour ago' % (delta.seconds / 3600)
    elif delta.seconds >= 120:
        return '%s mins ago' % (delta.seconds / 60)
    elif delta.seconds >= 60:
        return '1 min ago'
    else:
        return 'just now'
