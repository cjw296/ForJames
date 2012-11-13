'''
Created on Nov 10, 2012

@author: peterb
'''

from sqlalchemy.types import Integer, String
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.orm import relationship
from model.base import Base


class Person(Base):
    __tablename__ = "person"
    _list_view_ = ["id","email"]
    
    id = Column(Integer, primary_key=True)
    email = Column(String(80), unique=True, nullable=False)
    password = Column(String(80))

    permissions = relationship('Permission', 
                               secondary="person_permission", 
                               lazy='joined')
    
    
    def __repr__(self):
        return "<Person email=%r>" % self.email
    

    def has_permissions(self, permissions):
        for permission in self.permissions:
            if permission.name in permissions:
                return True
        return False


person_permission = Table('person_permission', Base.metadata,
    Column('person_id', Integer, ForeignKey('person.id')),
    Column('permission_id', Integer, ForeignKey('permission.id')),
    mysql_engine='InnoDB'
)
