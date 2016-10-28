# post for the first time: 'http://blog.kubernetes.io/2016/02/sharethis-kubernetes-in-production.html'
# out = get json response

# wait and maybe close the database connection / restart the database

# then post for the second time: 'http://blog.kubernetes.io/2016/02/sharethis-kubernetes-in-production.html'
# the output should be the same

import cherrypy
from cherrypy.test import helper

# from urllib.parse import urlparse
# from threading import Thread
# import http.client, sys
# from queue import Queue

# def test_rate_limit_403():

#     for _ in range(5):
#         conn = http.client.HTTPConnection(url.netloc)
#         conn.request("GET", url.path)
#         res = conn.getresponse()
#         print(res.status)


class SimpleCPTest(helper.CPWebCase):
    def setup_server():
        class Root(object):
            @cherrypy.expose
            def echo(self, message):
                return message

        cherrypy.tree.mount(Root())
    setup_server = staticmethod(setup_server)

    def test_message_should_be_returned_as_is(self):
        self.getPage("/url")
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'text/html;charset=utf-8')
        self.assertBody('Hello world')

    def test_non_utf8_message_will_fail(self):
        """
        CherryPy defaults to decode the query-string
        using UTF-8, trying to send a query-string with
        a different encoding will raise a 404 since
        it considers it's a different URL.
        """
        self.getPage("/echo?message=A+bient%F4t",
                     headers=[
                         ('Accept-Charset', 'ISO-8859-1,utf-8'),
                         ('Content-Type', 'text/html;charset=ISO-8859-1')
                     ]
        )
        self.assertStatus('404 Not Found')




# concurrent = 10

# def doWork():
#     while True:
#         url = q.get()
#         status, url = getStatus(url)
#         doSomethingWithResult(status, url)
#         q.task_done()

# def getStatus(ourl):
#     try:
#         url = urlparse(ourl)
#         conn = http.client.HTTPConnection(url.netloc)
#         conn.request("GET", url.path)
#         res = conn.getresponse()
#         return res.status, ourl
#     except Exception as e:
#         return "error", ourl, e

# def doSomethingWithResult(status, url):
#     print(status, url)

# q = Queue(concurrent * 2)
# for i in range(concurrent):
#     t = Thread(target=doWork)
#     t.daemon = True
#     t.start()
# try:
#     url = 'http://localhost:8080/url/1'
#     N = 40
#     for _ in range(N):
#         q.put(url.strip())
#     q.join()
# except KeyboardInterrupt:
#     sys.exit(1)
