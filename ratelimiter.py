# Most of this code is from:
# https://github.com/projectweekend/Falcon-PostgreSQL-API-Seed/blob/master/app/middleware/rate_limit.py
from time import time

import cherrypy
import redis


class RateLimiter(object):
    def __init__(self, limit=100, window=60):
        self.limit = limit
        self.window = window
        self.redis = redis.StrictRedis(host='redis', port=6379)

    def process_request(self, req, res):
        requester = cherrypy.request.headers['REMOTE_ADDR']
        requester = req.env['REMOTE_ADDR']

        # un-comment if you want to ignore calls from localhost
        # if requester == '127.0.0.1':
        #     return

        # key = "{0}: {1}".format(requester, req.path)
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
            'X-RateLimit-Reset: ': str(time() + expires_in)
        })

        if remaining > 0:
            self.redis.incr(key, 1)
        else:
            raise cherrypy.HTTPError(status=429, 'Blocked: Too many requests!')
