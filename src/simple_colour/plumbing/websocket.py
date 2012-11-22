'''
Created on Nov 22, 2012

@author: peterb
'''
from tornado.websocket import WebSocketHandler
from simple_colour.plumbing.control import Control
import json
import logging
import time
from simple_colour.plumbing.access_handler import AccessHandler


class WebSocket(WebSocketHandler):
    ''' 
        Using the default tornado WebSocket Handler 
    '''
    
    clients = []
    
    def open(self):
        if self.application.settings.get('login_url') and self.current_user is None:
            self.write_message(self.outgoing({
                                "error": "session expired",
                                "redirect": self.application.settings.login_url
                                }))
            return
        WebSocket.clients.append(self)
        

    def get_current_user(self):
        if self.application.settings.get('login_url'):
            result = AccessHandler.get_auth_user_from_cookie(self)
            logging.debug(result)
            return result


    def on_message(self, message):  
        if self.application.settings.get('login_url') and self.current_user is None:
            return  
        started = time.time()
            
        message = json.loads(message)
        request_id = message.get('request_id')
        method = message.get("method")
        kwargs = message.get("kwargs")
                
        try:
            self.on_result(method, 
                           request_id, 
                           Control.CONTROL._perform_(method, 
                                                     kwargs, 
                                                     self.current_user))
            for signal, message in Control.CONTROL._to_broadcast_:
                broadcast = json.dumps({"signal":signal,
                                        "message": message})
                self.broadcast(WebSocket.clients, broadcast)
        except Exception,ex:
            logging.exception(ex)
            self.on_result(method, request_id, error=str(ex))
            
        request_time = 1000.0 * (time.time() - started)
        logging.info("%s %.2fms", message, request_time )
        
        
    def on_close(self):
        if self in WebSocket.clients:
            WebSocket.clients.remove(self)
    
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
            