import cherrypy
from cherrypy.process import wspbus, plugins
from redis import StrictRedis
import string

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
    def __init__(self):
        self.store = StrictRedis(host='redis', port=6379, db=0, decode_responses=True)
        self.urlprefix = 'url:'
        self.codeprefix = 'code:'

    def shorten(self, url):
        # other way for larger number of inputs to use b64 of md5
        urlcode = self.store.get((self.codeprefix + url))
        print('shorten urlcode get:', urlcode)
        if urlcode is not None:
            print('early return: ', urlcode)
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
