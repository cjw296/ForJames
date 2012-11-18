'''
    This will contain a common model for these sample applications, sorry, I'm lazy.
'''

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.exc import IntegrityError
import logging
from model.base import Base
from model.permission import Permission
from model.person import Person
from model.pages import Page

def create_initialize_db(db_url, echo=False):
    engine = create_engine(db_url, echo=echo)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    
    session = Session()
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
    finally:
        session.close()
        
    return Session, engine