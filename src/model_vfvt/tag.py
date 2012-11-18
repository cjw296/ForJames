'''
Created on Nov 18, 2012

@author: peterb
'''

from sqlalchemy.types import String
from sqlalchemy.schema import Column
from model_vfvt.base import Base,ValidFromValidTo, Find_or_Create_by_Name_On

class Tag(Base, ValidFromValidTo, Find_or_Create_by_Name_On):
    
    name = Column(String(80), nullable=False)

