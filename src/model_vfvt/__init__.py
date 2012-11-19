'''
    This will contain a common model for these sample applications, sorry, I'm lazy.
'''

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import Index
import logging

from model_vfvt.base import Base, VersionExtension, Reference
from model_vfvt.tag import Tag
from model_vfvt.page import Page, PageTag
from model_vfvt.permission import Permission
from model_vfvt.person import Person, PersonPermission

Index("tag_ref",Tag.ref,Tag.valid_from,Tag.valid_to)
Index("page_ref",Page.ref,Page.valid_from,Page.valid_to)
Index("page_tag_ref",PageTag.ref,PageTag.valid_from,PageTag.valid_to)
Index("permission_ref",Permission.ref,Permission.valid_from,Permission.valid_to)
Index("person_ref",Person.ref,Person.valid_from,Person.valid_to)
Index("person_permission_ref",PersonPermission.ref,PersonPermission.valid_from,PersonPermission.valid_to)


def create_initialize_db(db_url, echo=False):
    engine = create_engine(db_url, echo=echo)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(engine,extension=[VersionExtension()])
    session = Session()
    try:
        if Permission.by_ref(session, 1) is None:
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