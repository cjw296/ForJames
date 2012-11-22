'''
Created on Nov 22, 2012

@author: peterb
'''
import logging
import inspect

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import and_
from sqlalchemy.orm import joinedload_all
from simple_colour.plumbing.user import User
from simple_colour.plumbing.model import Base
from simple_colour.plumbing import model
from sqlalchemy.exc import IntegrityError



def requires_permission(permissions):
    ''' This annotation tells the service which permissions are rquired to perform the function '''
    def _require(f):            
        def call(self, *args, **kwargs):
            self._require_permission_(*permissions)
            result = f(self, *args, **kwargs)
            return result
        call._wrapped_ = f
        call._service_permissions_ = permissions
        return call
    return _require


class Control(object):
    ''' 
        The stuff you don't need to see - just assume it's there. 
    '''
    
    CONTROL = None # singleton, because SockJSConnection is not a Handler, sadly

    
    def __init__(self, db_url="sqlite://", echo=False):
        self._engine = create_engine(db_url, echo=echo)
        Base.metadata.create_all(self._engine)
        self._Session = sessionmaker(self._engine)
        self._to_broadcast_ = []
        self._accl_key_ = None
        self._user_ = None
        Control.CONTROL = self
        with self._session_context as session:
            self._init_db_(session)
        
        
    def _dispose_(self):
        ''' tidy up we've gone away '''
        self._engine.dispose()
        self._Session = self._engine = None
        logging.debug("control disposed")
        
        
    def _init_db_(self, session):
        try:
            permissions = [model.Permission(name=name) for name in model.Permission.ROLES]
            session.add_all(permissions)
            
            admin = model.Person(email="admin",password="admin")       
            user = model.Person(email="user",password="user")
            
            session.add_all([admin, user])
            
            admin.permissions.append(permissions[0])
            admin.permissions.append(permissions[1])
            user.permissions.append(permissions[1])
                
            session.commit()
        except IntegrityError:
            pass
        except Exception, ex:
            logging.warn(ex)
            raise
        
        
    @classmethod
    def _describe_service_(cls, obj):
        '''Returns a description of the public methods of this class'''
        
        methods = []
        for name in dir(obj):
            if name[0] == '_': continue
            method = getattr(obj,name)
            requires = []
            if hasattr(method,'_service_permissions_'):
                requires = method._service_permissions_
                method = method._wrapped_
            if callable(method):
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
    def _session(self):    
        return self._Session()
        
    @property
    def _session_context(self):
        ''' returns a self closing session '''
        session = self._session
        class closing_session:
            def __enter__(self):
                logging.debug("session open")
                return session
            def __exit__(self, type, value, traceback):
                logging.debug("session closed")
                session.close()
        return closing_session()
    
    
    def _perform_(self, method_name, kwargs={}, accl_key=None):
        ''' Used to dispatch rpc '''
        self._to_broadcast_ = []
        self._accl_key_ = accl_key
        if method_name[0] != "_" and hasattr(self, method_name) and callable(getattr(self,method_name)):
            return getattr(self,method_name)(**kwargs)
        else:
            self._to_broadcast_ = []
            raise Exception("No such method '%s'!" % method_name)
        
        
    def _broadcast_on_success_(self, signal, **kwargs):
        ''' cache message until transaction closes cleanly '''
        self._to_broadcast_.append((signal,kwargs))

    ''' Access Control '''
        
    def _login_(self, email, password):
        with self.session_context as session:
            person = session.query(model.Person).filter(and_(model.Person.email==email,
                                                             model.Person.password==password)).first()
            if person is None:
                raise Exception("Email or password incorrect!")
            return person.id

    @property
    def _accl_key(self):
        return self._accl_key_
    
    @property
    def _user(self):
        if self._user_ is None:
            self._user_ = self._load_user_(self._accl_key)
        return self._user_


    def _load_user_(self, id):
        with self._session_context as session:
            person = session.query(model.Person).\
                              options(joinedload_all(model.Person.permissions)).get(id)
            if person:
                result = User(person.id, 
                              person.email,
                              [p.name for p in person.permissions])
                return result
        
        
    def _require_permission_(self, *args):
        '''
            Given the users persmissions.
            When the user has none of the permissions in args.
            Then raise an exception.
        '''
        if self._user.has_permissions(*args) is False:
            raise Exception("You do not have permission for this action.")
