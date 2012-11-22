'''
Created on Nov 22, 2012

@author: peterb
'''
from pkg_resources import resource_filename
from tornado import web, ioloop, options, websocket
from sockjs.tornado import SockJSRouter, SockJSConnection
from simple_colour import model
from simple_colour.control import Control
import logging
import time
import json


class ColourWebSocket(websocket.WebSocketHandler):
    
    def open(self):
        self.application.clients.append(self)
        logging.debug("session open")
        
    def on_close(self):
        if self in self.application.clients:
            self.application.clients.remove(self)
        logging.debug("session closed")
        

    def on_message(self, message):    
        started = time.time()
            
        message = json.loads(message)
        request_id = message.get('request_id')
        method = message.get("method")
        kwargs = message.get("kwargs")
                
        try:
            self.on_result(method, request_id, self.application.control._perform_(method, kwargs))
            for signal, message in self.application.control._to_broadcast_:
                broadcast = json.dumps({"signal":signal,"message": message})
                self.broadcast(self.application.clients, broadcast)
        except Exception,ex:
            logging.exception(ex)
            self.on_result(method, request_id, error=str(ex))
            
        request_time = 1000.0 * (time.time() - started)
        logging.info("%s %.2fms", message, request_time )
    
    def on_result(self, method, request_id, result=None, error=None):
            self.write_message(json.dumps({
                                  "method": method,
                                  "result": result,
                                  "error": error,
                                  "request_id": request_id
                                 }))
            
    def broadcast(self, clients, message):
        for client in clients:
            client.write_message(message)
            logging.debug('wrote %s', message)


class WSHandler(SockJSConnection):
    clients = []
    
    def on_open(self, request):
        WSHandler.clients.append(self)
        
    def on_close(self):
        WSHandler.clients.remove(self)
        

    def on_message(self, message):    
        started = time.time()
            
        message = json.loads(message)
        request_id = message.get('request_id')
        method = message.get("method")
        kwargs = message.get("kwargs")
                
        try:
            self.on_result(method, request_id, Control.CONTROL._perform_(method, kwargs))
            for signal, message in Control.CONTROL._to_broadcast_:
                broadcast = json.dumps({"signal":signal,"message": message})
                print broadcast
                self.broadcast(WSHandler.clients, broadcast)
        except Exception,ex:
            logging.exception(ex)
            self.on_result(method, request_id, error=str(ex))
            
        request_time = 1000.0 * (time.time() - started)
        logging.info("%s %.2fms", message, request_time )
    
    def on_result(self, method, request_id, result=None, error=None):
            self.send(json.dumps({
                                  "method": method,
                                  "result": result,
                                  "error": error,
                                  "request_id": request_id
                                 }))

        
class MainHandler(web.RequestHandler):

    def get(self):
        self.render("index.html")

class Appl_JS_Handler(web.RequestHandler):

    def get(self):
        self.add_header("content-type", "text/javascript")
        self.render("appl.js", description=Control._describe_service_(Control))


def main():
    options.parse_command_line()
    WSRouter = SockJSRouter(WSHandler, '/sockjs')
    handlers = [
        (r'/', MainHandler),
        (r'/appl.js', Appl_JS_Handler),
        (r'/websocket', ColourWebSocket)
    ] + WSRouter.urls

    appl = web.Application(handlers,
                           static_path=resource_filename("web","www/static"),
                           template_path=resource_filename("simple_colour","templates"),
                           debug=True)
    appl.control = Control(model.Base)
    appl.clients = []
    appl.listen(8080)
    logging.info('listening on port 8080')
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()