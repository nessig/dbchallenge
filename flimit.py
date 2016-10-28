import time
from functools import update_wrapper
import cherrypy
import json

# def get_identifiers():
#     ret = ['ip:' + request.remote_addr]
#     return ret

# def over_limit_multi_lua(conn, limits=[(1, 10), (60, 125), (3600, 250)]):
#     if not hasattr(conn, 'over_limit_multi_lua'):
#         conn.over_limit_multi_lua = conn.register_script(over_limit_multi_lua_)

#     return conn.over_limit_multi_lua(
#         keys=get_identifiers(), args=[json.dumps(limits), time.time()])

# over_limit_multi_lua_ = '''
# local limits = cjson.decode(ARGV[1])
# local now = tonumber(ARGV[2])
# for i, limit in ipairs(limits) do
#     local duration = limit[1]

#     local bucket = ':' .. duration .. ':' .. math.floor(now / duration)
#     for j, id in ipairs(KEYS) do
#         local key = id .. bucket

#         local count = redis.call('INCR', key)
#         redis.call('EXPIRE', key, duration)
#         if tonumber(count) > limit[2] then
#             return 1
#         end
#     end
# end
# return 0
# '''

# class RateLimit(object):
#     expiration_window = 10

#     def __init__(self, key_prefix, limit, per, send_x_headers):
#         self.reset = (int(time.time()) // per) * per + per
#         self.key = key_prefix + str(self.reset)
#         self.limit = limit
#         self.per = per
#         self.send_x_headers = send_x_headers
#         p = redis.pipeline()
#         p.incr(self.key)
#         p.expireat(self.key, self.reset + self.expiration_window)
#         self.current = min(p.execute()[0], limit)

#     remaining = property(lambda x: x.limit - x.current)
#     over_limit = property(lambda x: x.current >= x.limit)

# def get_view_rate_limit():
#     return getattr(g, '_view_rate_limit', None)

# def on_over_limit(limit):
#     return 'You hit the rate limit', 400

# def ratelimit(limit, per=300, send_x_headers=True,
#               over_limit=on_over_limit,
#               scope_func=lambda: request.remote_addr,
#               key_func=lambda: request.path_info):
#     def decorator(f):
#         def rate_limited(*args, **kwargs):
#             key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
#             rlimit = RateLimit(key, limit, per, send_x_headers)
#             g._view_rate_limit = rlimit
#             if over_limit is not None and rlimit.over_limit:
#                 return over_limit(rlimit)
#             return f(*args, **kwargs)
#         return update_wrapper(rate_limited, f)
#     return decorator


class RateLimiter(cherrypy.Tool):
    def __init__(self, limit=100, window=60):
        cherrypy.Tool.__init__(self, 'before_handler',
                               self.load, priority=10)
        self.limit = limit
        self.window = window
        self.redis = redis.StrictRedis(host='localhost', port=6379)

    def process_request(self, req, res):
        requester = cherrypy.request.remote_addr

        # un-comment if you want to ignore calls from localhost
        if requester == '127.0.0.1':
            return

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
            raise cherrypy.HTTPError(status=403, 'Blocked: Too many requests!')
