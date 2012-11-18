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


class Page(Base, ValidFromValidTo):
    
    title = Column(String(80), nullable=False)
    content = Column(Text())
    owner_ref = Column(Integer)
    
    def _get_owner_(self):
        if self.owner_ref is None:
            return None
        session = object_session(self)
        query = session.query(Person).filter(and_(Person.ref==self.owner_ref,
                                                 Person.valid_on()))
        return query.first()
                                                 
    def _set_owner_(self, value):
        if value.ref is None:
            raise Exception("Set relation before added to session")
        self.owner_ref = value.ref
    
    owner = property(_get_owner_, _set_owner_)
    
    
    def add_tag(self, tag):
        if self.ref is None or tag.ref is None:
            raise Exception("Add to relation on versioned object before adding to session")
        session = object_session(self)
        session.add(PageTag(page_ref=self.ref, tag_ref=tag.ref))
        
    
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
    
    