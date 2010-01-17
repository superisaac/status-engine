
# Page sizes for SimplePaginator
BLIP_PAGE_SIZE = 20
ROOM_PAGE_SIZE = 20

# Login method, options are: local, google, both
LOGIN_METHOD = 'both'

# news user account email and password
# redefine it at local_settings please
NEWS_USER = 'news@example.com'
NEWS_PASSWORD = 'news'

# Google map key
# Please apply it through http://code.google.com/apis/maps/signup.html
MAP_KEY = 'ABQIAAAADsnbaFl-RI5O69x2LuN9JhRIqEmBdYeQiVoecy_u8nwJh2CJchT_L4HyqzqD_8kDEddc0K0N-JCvHw' # for http://status-engine.appspot.com

try:
    from local_settings import *
except ImportError:
    pass
