'''
Created on Nov 22, 2012

@author: peterb
'''
import logging
import inspect
        
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
    

from sockjs.tornado import SockJSConnection
from tornado.websocket import WebSocketHandler
import tornado.web
import time
import json


class Control(object):
    ''' 
        The stuff you don't need to see - just assume it's there. 
    '''
    
    CONTROL = None # singleton, because SockJSConnection is not a Handler, sadly

    
    def __init__(self, Base, db_url="sqlite://", echo=False):
        self._engine = create_engine(db_url, echo=echo)
        Base.metadata.create_all(self._engine)
        self._Session = sessionmaker(self._engine)
        self._to_broadcast_ = []
        Control.CONTROL = self
        
    def _dispose_(self):
        ''' tidy up we've gone away '''
        self._engine.dispose()
        self._Session = self._engine = None
        logging.debug("control disposed")
        
        
    @classmethod
    def _describe_service_(cls, obj):
        '''Returns a description of the public methods of this class'''
        
        methods = []
        for name in dir(obj):
            method = getattr(obj,name)
            requires = []
            if hasattr(method,'_service_permissions_'):
                requires = method._service_permissions_
                method = method._wrapped_
            if name[0] != "_" and callable(method):
                spec = inspect.getargspec(method)
                args = [n for n in spec.args if n not in ('self')]
                logging.debug('%s %s',name,inspect.formatargspec(spec))
                defaults = {}
                if spec.defaults:
                    sdefaults = list(spec.defaults)
                    sdefaults.reverse()
                    for i,value in enumerate(sdefaults):
                        defaults[spec.args[-(i+1)]] = value if value is not None else '_optional_'
                docs = inspect.getdoc(method)
                description = {
                               "name":name, 
                               "args": args, 
                               "defaults": defaults,
                               "requires": requires, 
                               "docs": docs
                               }
                methods.append(description)
        return methods

        
        
    @property
    def session(self):
        ''' returns a self closing session '''
        session = self._Session()
        class closing_session:
            def __enter__(self):
                logging.debug("session open")
                return session
            def __exit__(self, type, value, traceback):
                logging.debug("session closed")
                session.close()
        return closing_session()
    
    
    def _perform_(self, method_name, kwargs={}):
        ''' Used to dispatch rpc '''
        self._to_broadcast_ = []
        if method_name[0] != "_" and hasattr(self, method_name) and callable(getattr(self,method_name)):
            return getattr(self,method_name)(**kwargs)
        else:
            self._to_broadcast_ = []
            raise Exception("No such method '%s'!" % method_name)
        
        
    def _broadcast_on_success_(self, signal, **kwargs):
        ''' cache message until transaction closes cleanly '''
        self._to_broadcast_.append((signal,kwargs))
        
        
class _OnMessageMixin_(object):
    ''' 
        Avoiding duplication 
    '''
        
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
                self.broadcast(WebSocket.clients, broadcast)
        except Exception,ex:
            logging.exception(ex)
            self.on_result(method, request_id, error=str(ex))
            
        request_time = 1000.0 * (time.time() - started)
        logging.info("%s %.2fms", message, request_time )
        


class WebSocket(_OnMessageMixin_,WebSocketHandler):
    ''' 
        Using the default tornado WebSocket Handler 
    '''
    
    clients = []
    
    def open(self):
        WebSocket.clients.append(self)
        
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



class Connection(_OnMessageMixin_,SockJSConnection):
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


class JSHandler(tornado.web.RequestHandler):
    ''' 
        A self describing Control expresses as a tornado template, 
        sent back as javascript
    '''
    def get(self):
        self.add_header("content-type", "text/javascript")
        self.render("appl.js", description=Control._describe_service_(Control.CONTROL))
        
    