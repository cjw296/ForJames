'''
Created on Nov 18, 2012

@author: peterb
'''

from sqlalchemy.types import String
from sqlalchemy.schema import Column
from model_vfvt.base import Base,ValidFromValidTo

class Tag(Base, ValidFromValidTo):
    
    name = Column(String(80), nullable=False)
