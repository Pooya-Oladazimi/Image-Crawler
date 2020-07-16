import socket, ssl, sys
from imageCrawler import Crawler

target = sys.argv[1]
limit = sys.argv[2]
crawl = Crawler(socket, str(target), ssl, int(limit))
crawl.main()


