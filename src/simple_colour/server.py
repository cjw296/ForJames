'''
Created on Nov 22, 2012

@author: peterb
'''
from pkg_resources import resource_filename
from tornado import web, ioloop, options
from sockjs.tornado import SockJSRouter
from simple_colour import plumbing
from simple_colour import model
from simple_colour.control import Control
import logging

options.define("port", 8080, type=int, help="server port number (default: 8080)")
options.define("db_url", 'sqlite://', help="sqlalchemy db url")

def main():
    ''' parse the command line - new up the appl and listen on port '''
    options.parse_command_line()
    WSRouter = SockJSRouter(plumbing.Connection, '/sockjs')
    handlers = [
        (r'/', plumbing.IndexHandler),
        (r"/login", plumbing.AccessHandler),
        (r'/appl.js', plumbing.ApplJsHandler),
        (r'/websocket', plumbing.WebSocket)
    ] + WSRouter.urls

    appl = web.Application(handlers,
                           static_path=resource_filename("web","www/static"),
                           template_path=resource_filename("simple_colour","templates"),
                           login_url="/login",
                           cookie_secret="hello_simple_colour_secret",
                           debug=True)
    appl.control = Control(options.options.db_url)
    appl.ACCESS_COOKIE_NAME = "simple_colour_session"
    
    appl.listen(options.options.port)
    logging.info('listening on port %s', options.options.port)
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()