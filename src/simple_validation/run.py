'''
This is from: http://www.tornadoweb.org

I've changed the port to 8080 as that is what I'm used to...

Just select web.py and choose 'Run As / Python Run' from the Run menu.

Then open your browser to http://localhost:8080

Created on Nov 13, 2012

@author: peterb
'''
from pkg_resources import resource_filename  # we use this to make our paths relative to our packages!
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

def run():
    static_path=resource_filename("web","www/static")
    template_path=resource_filename("simple_validation","/")
    
    application = tornado.web.Application([
        (r"/", MainHandler),
    ], static_path=static_path,
       template_path=template_path,
       debug=True)
    
    application.listen(8080)
    print "listening on 8080"
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    run()