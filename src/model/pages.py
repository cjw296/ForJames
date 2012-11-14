'''
Created on Nov 14, 2012

@author: peterb
'''

from sqlalchemy.types import Integer, String
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.orm import relationship
from model.base import Base


class Page(Base):
    __tablename__ = "page"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(80), unique=True, nullable=False)
    content = Column(String(80))

    ''' one to many relation ''' 
    owner_id = Column(Integer, ForeignKey('person.id'))
    owner = relationship('Person', 
                         remote_side='person.c.id', 
                         back_populates="pages")

    def __repr__(self):
        return "<Person email=%r>" % self.email
    

    def has_permissions(self, permissions):
        for permission in self.permissions:
            if permission.name in permissions:
                return True
        return False

