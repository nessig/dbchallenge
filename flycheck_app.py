import os, os.path
import json
import cherrypy
import urlshortener

def error_page_default(status, message, traceback, version):
    """Nice JSON error handler"""
    ret = {
        'status': status,
        'version': version,
        'message': [message],
        'traceback': traceback
    }
    return json.dumps(ret)

class Root(object):
    """Index view"""
    @cherrypy.expose
    def index(self):
        return open('index.html')


@cherrypy.expose
class UrlGeneratorWebService(object):
    """Url shorter web service"""
    _cp_config = {'error_page.default': error_page_default}
    PREFIX = '/url/'

    @cherrypy.tools.json_out()
    @cherrypy.popargs('urlcode')
    def GET(self, urlcode=None):
        url = cherrypy.engine.publish('db-get', urlcode)[0]
        if url is None:
            # sanitize the url input here
            raise cherrypy.HTTPError(404, "Not Found: the url {} was not found".format(url))
        print('url: ', url)
        print('urlcode: ', urlcode)
        raise cherrypy.HTTPRedirect(url)

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        data = cherrypy.request.json
        if 'url' not in data:
            raise cherrypy.HTTPError(400, 'Bad Request: missing JSON data in request')
        url = data['url']
        urlcode = cherrypy.engine.publish('db-shorten', url)[0]
        print('url: ', url)
        print('urlcode: ', urlcode)
        return {'urlcode': self.PREFIX + urlcode}

cherrypy.config.update({
    'server.socket_host': '0.0.0.0', #if you are running this on ec2, uncomment!
    'server.socket_port': 80,      #so you can access by host address
    'server.thread_pool': 10, # 10 is default
    'tools.trailing_slash.on': False # True is default
})

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
        },
        '/url': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

    urlshortener.DatabasePlugin(cherrypy.engine, urlshortener.ShortenUrlService).subscribe()

    webapp = Root()
    webapp.url = UrlGeneratorWebService()
    cherrypy.quickstart(webapp, '/', conf)
