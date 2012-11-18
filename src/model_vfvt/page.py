'''
Created on Nov 18, 2012

@author: peterb
'''
from sqlalchemy.types import String, Integer, Text
from sqlalchemy.schema import Column
from sqlalchemy.orm import object_session

from model_vfvt.base import Base,ValidFromValidTo
from model_vfvt.tag import Tag
from sqlalchemy.sql.expression import and_
from model_vfvt.person import Person
import datetime


class Page(Base, ValidFromValidTo):
    
    title = Column(String(80), nullable=False)
    content = Column(Text())
    
    ''' Owner Support '''    
    owner_ref = Column(Integer)

    @property
    def owner(self):
        if self.owner_ref is None:
            return None
        session = object_session(self)
        query = session.query(Person).filter(and_(Person.ref==self.owner_ref,
                                                 Person.valid_on()))
        return query.first()
    
    @owner.setter                                        
    def owner(self, value):
        if value is None:
            self.owner_ref = None
        elif value.ref is None:
            raise Exception("Set relation before added to session")
        else:
            self.owner_ref = value.ref
    
        
    ''' Tag support '''
    def add_tag(self, tag):
        if self.ref is None or tag.ref is None:
            raise Exception("Add to relation on versioned object before adding to session")
        session = object_session(self)
        session.add(PageTag(page_ref=self.ref, tag_ref=tag.ref))
            
    def remove_tag(self, tag, on_date=None):
        if self.ref is None or tag.ref is None:
            raise Exception("Remove from relation on versioned object before adding to session")
        session = object_session(self)
        page_tag = session.query(PageTag.tag_ref).filter(and_(PageTag.page_ref==self.ref,
                                                              PageTag.tag_ref==tag.ref,
                                                              PageTag.valid_on())).first()
        if page_tag is not None:
            page_tag.valid_to = on_date if on_date is not None else datetime.datetime.now()
    
    @property
    def tags(self):
        session = object_session(self)
        subselect = session.query(PageTag.tag_ref).filter(and_(PageTag.page_ref==self.ref,
                                                               PageTag.valid_on()))
        query = session.query(Tag).filter(and_(Tag.ref.in_(subselect),
                                               Tag.valid_on()))
        return query


class PageTag(Base, ValidFromValidTo):
    
    page_ref = Column(Integer)
    tag_ref = Column(Integer)
    
    