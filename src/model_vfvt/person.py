'''
Created on Nov 18, 2012

@author: peterb
'''

from sqlalchemy.types import String
from sqlalchemy.schema import Column, Index
from model_vfvt.base import Base,ValidFromValidTo

class Person(Base, ValidFromValidTo):
    
    email = Column(String(80), nullable=False)
    password = Column(String(80))


Index('person_unique_email', Person.ref, Person.email, unique=True)