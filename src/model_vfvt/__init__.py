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
from model_vfvt.person import Person


def create_initialize_db(db_url, echo=False):
    engine = create_engine(db_url, echo=echo)
    Base.metadata.create_all(engine)
#    Index("tag_ref",Tag.ref,Tag.valid_from,Tag.valid_to)
#    Index("page_ref",Page.ref,Page.valid_from,Page.valid_to)
#    Index("page_tag_ref",PageTag.ref,PageTag.valid_from,PageTag.valid_to)
#    Index("person_ref",Person.ref,Person.valid_from,Person.valid_to)
    
    Session = sessionmaker(engine,extension=[VersionExtension()])
            
    return Session, engine