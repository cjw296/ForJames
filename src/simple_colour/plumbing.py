'''
Created on Nov 22, 2012

@author: peterb
'''
import logging
import inspect
        
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
    


class SessionControl(object):
    CONTROL = None # singleton

    
    def __init__(self, Base, db_url="sqlite://", echo=False):
        self._engine = create_engine(db_url, echo=echo)
        Base.metadata.create_all(self._engine)
        self._Session = sessionmaker(self._engine)
        self._to_broadcast_ = []
        SessionControl.CONTROL = self
        
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
        