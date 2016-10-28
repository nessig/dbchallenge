# post for the first time: 'http://blog.kubernetes.io/2016/02/sharethis-kubernetes-in-production.html'
# out = get json response

# wait and maybe close the database connection / restart the database

# then post for the second time: 'http://blog.kubernetes.io/2016/02/sharethis-kubernetes-in-production.html'
# the output should be the same

from urllib.parse import urlparse
from threading import Thread
import http.client, sys
from queue import Queue

def test_rate_limit_403():
    for _ in range(5):
        conn = http.client.HTTPConnection(url.netloc)
        conn.request("GET", url.path)
        res = conn.getresponse()
        res.status



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
