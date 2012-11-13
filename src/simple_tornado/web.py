'''
This is from: http://www.tornadoweb.org

I've changed the port to 8080 as that is what I'm used to...

Just select web.py and choose 'Run As / Python Run' from the Run menu.

Then open your browser to http://localhost:8080

Created on Nov 13, 2012

@author: peterb
'''

import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8080)
    print "listening on 8080"
    tornado.ioloop.IOLoop.instance().start()