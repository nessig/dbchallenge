import cherrypy
from cherrypy.process import wspbus, plugins
from redis import StrictRedis
import os
import string
import time

BASE_LIST = string.digits + string.ascii_letters + '_@'

def base_encode(integer, base=BASE_LIST):
    if integer == 0:
        return base[0]

    length = len(base)
    ret = ''
    while integer != 0:
        ret = base[integer % length] + ret
        integer //= length

    return ret

class ShortenUrlService(object):
    def __init__(self, host='redis', port=6379, db=0):
        host = os.environ.get('DATABASE_HOST', 'redis')
        self.store = StrictRedis(host=host, port=port, db=db, decode_responses=True)
        self.urlprefix = 'url:'
        self.codeprefix = 'code:'

    def shorten(self, url):
        # other way for larger number of inputs to use b64 of md5
        urlcode = self.store.get((self.codeprefix + url))
        if urlcode is not None:
            return urlcode
        urlcount = self.store.incr('url-count')
        urlcode = base_encode(urlcount)
        self.store.set(self.urlprefix + urlcode, url)
        self.store.set(self.codeprefix + url, urlcode)
        return urlcode

    def get(self, urlcode):
        try:
            return self.store.get(self.urlprefix + urlcode)
        except:
            return None


class TimingTool(cherrypy.Tool):
    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_handler',
                               self.start_timer,
                               priority=95)

    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('before_finalize',
                                      self.end_timer,
                                      priority=5)

    def start_timer(self):
        cherrypy.request._time = time.time()

    def end_timer(self):
        duration = time.time() - cherrypy.request._time
        cherrypy.log("Page handler took %.4f" % duration)


class RateLimiter(cherrypy.Tool):
    def __init__(self, limit=100, window=60):
        cherrypy.Tool.__init__(self, 'before_handler',
                               self.process_request, priority=10)
        cherrypy.log("Creating rate limiter with limit={} and window={}".format(limit, window))
        self.limit = limit
        self.window = window
        self.redis = StrictRedis(host='redis', port=6379)

    def process_request(self):
        print(cherrypy.request)
        print(cherrypy.request.remote)
        requester = cherrypy.request.remote.ip
        print("remote:", requester)

        # un-comment if you want to ignore calls from localhost
        # if requester == '127.0.0.1':
        #     return

        key = "{0}: {1}".format(requester, cherrypy.request.path_info)
        print('Key: {0}'.format(key))

        try:
            remaining = self.limit - int(self.redis.get(key))
        except (ValueError, TypeError):
            remaining = self.limit
            self.redis.set(key, 0)

        expires_in = self.redis.ttl(key)

        if expires_in == -1:
            self.redis.expire(key, self.window)
            expires_in = self.window

        cherrypy.request.headers.update({
            'X-RateLimit-Remaining: ': str(remaining - 1),
            'X-RateLimit-Limit: ': str(self.limit),
            'X-RateLimit-Reset: ': str(time.time() + expires_in)
        })

        if remaining > 0:
            self.redis.incr(key, 1)
        else:
            raise cherrypy.HTTPError(429, 'Blocked: Too many requests!')


class DatabasePlugin(plugins.SimplePlugin):
    def __init__(self, bus, db_klass):
        plugins.SimplePlugin.__init__(self, bus)
        self.db = db_klass()

    def start(self):
        self.bus.log('Starting up DB access')
        self.bus.subscribe("db-shorten", self.shorten)
        self.bus.subscribe("db-get", self.get)

    def stop(self):
        self.bus.log('Stopping down DB access')
        self.bus.unsubscribe("db-shorten", self.shorten)
        self.bus.unsubscribe("db-get", self.get)

    def shorten(self, url):
        return self.db.shorten(url)

    def get(self, key):
        return self.db.get(key)
