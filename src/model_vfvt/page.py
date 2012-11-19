'''
Created on Nov 18, 2012

@author: peterb
'''
from sqlalchemy.types import String, Integer, Text
from sqlalchemy.schema import Column
from sqlalchemy.orm import object_session

from model_vfvt.base import Base,ValidFromValidTo, _M2MCollection_
from model_vfvt.tag import Tag
from sqlalchemy.sql.expression import and_
from model_vfvt.person import Person


class Page(Base, ValidFromValidTo):
    
    title = Column(String(80), nullable=False)
    content = Column(Text())
    
    @property
    def label(self):
        return self.title.lower().replace(' ','_')

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
        
    @property
    def tags(self):
        return _M2MCollection_(self,Tag,PageTag)


class PageTag(Base, ValidFromValidTo):
    
    from_ref = Column(Integer)
    to_ref = Column(Integer)
    
    