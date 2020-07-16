import socket, ssl, sys
from imageCrawler import Crawler

if len(sys.argv) == 1:
    print("You need to specify a web page url as the target!")
    sys.exit()
target = sys.argv[1]
limit = 20
if len(sys.argv) == 3:
    limit = sys.argv[2]

crawl = Crawler(socket, str(target), ssl, int(limit))
crawl.main()


