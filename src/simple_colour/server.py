'''
Created on Nov 22, 2012

@author: peterb
'''
from pkg_resources import resource_filename
from tornado import web, ioloop, options
from sockjs.tornado import SockJSRouter
from simple_colour import model
from simple_colour.control import Control
from simple_colour import plumbing
import logging

options.define("port", 8080, type=int, help="server port number (default: 8080)")
options.define("db_url", 'sqlite:///simple_publish_vfvt.db', help="sqlalchemy db url")

class MainHandler(web.RequestHandler):
    ''' Returns our index.html from templates folder '''
    def get(self):
        self.render("index.html")


def main():
    ''' parse the command line - new up the appl and listen on port '''
    options.parse_command_line()
    WSRouter = SockJSRouter(plumbing.Connection, '/sockjs')
    handlers = [
        (r'/', MainHandler),
        (r'/plumbing', plumbing.JSHandler),
        (r'/websocket', plumbing.WebSocket)
    ] + WSRouter.urls

    appl = web.Application(handlers,
                           static_path=resource_filename("web","www/static"),
                           template_path=resource_filename("simple_colour","templates"),
                           debug=True)
    appl.control = Control(model.Base, options.options.db_url)
    appl.listen(options.options.port)
    logging.info('listening on port %s', options.options.port)
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()