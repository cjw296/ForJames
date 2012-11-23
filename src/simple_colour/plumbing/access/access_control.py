'''
Created on Nov 22, 2012

@author: peterb
'''


from sqlalchemy.sql.expression import and_
from sqlalchemy.orm import joinedload_all
from simple_colour.plumbing.access.user import User
from simple_colour.plumbing.core import model
from sqlalchemy.exc import IntegrityError
from simple_colour.plumbing.core.control import Control
from simple_colour.plumbing.access.person import Person, Permission
import logging


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



class AccessControl(Control):
    

    ''' Access Control '''
    
    def _init_db_(self, session):
        try:
            permissions = [Permission(name=name) for name in Permission.ROLES]
            session.add_all(permissions)
            
            admin = Person(email="admin",password="admin")       
            user = Person(email="user",password="user")
            
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

        
    def _login_(self, email, password):
        with self._session_context as session:
            person = session.query(Person).filter(and_(Person.email==email,
                                                       Person.password==password)).first()
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
            person = session.query(Person).\
                              options(joinedload_all(Person.permissions)).get(id)
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
