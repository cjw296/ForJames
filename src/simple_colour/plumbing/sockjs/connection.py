'''
Created on Nov 22, 2012

@author: peterb
'''

from sockjs.tornado import SockJSConnection
import json
from simple_colour.plumbing.access.access_handler import AccessHandler
import logging
import time
from simple_colour.plumbing.core.control import Control



class Connection(SockJSConnection):
    ''' 
        Using the SockJS WebSocket Connection 
    '''
    
    clients = []
    
    def on_open(self, request):
        Connection.clients.append(self)
        
    def on_close(self):
        if self in Connection.clients:
            Connection.clients.remove(self)
        
    
    def on_result(self, method, request_id, result=None, error=None):
            self.send(json.dumps({
                                  "method": method,
                                  "result": result,
                                  "error": error,
                                  "request_id": request_id
                                 }))

    def get_current_user(self):
        if self.application.settings.get('login_url'):
            result = AccessHandler.get_auth_user_from_cookie(self)
            logging.debug(result)
            return result


    def on_message(self, message):  
        if self.application.settings.get('login_url') and not self.current_user:
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
                self.broadcast(Connection.clients, broadcast)
        except Exception,ex:
            logging.exception(ex)
            self.on_result(method, request_id, error=str(ex))
            
        request_time = 1000.0 * (time.time() - started)
        logging.info("%s %.2fms", message, request_time )
