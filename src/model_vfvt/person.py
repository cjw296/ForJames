'''
Created on Nov 18, 2012

@author: peterb
'''

from sqlalchemy.types import String, Integer
from sqlalchemy.schema import Column
from model_vfvt.base import Base,ValidFromValidTo, Find_or_Create_by_Name_On,\
    _M2MCollection_

from model_vfvt.permission import Permission

class Person(Base, ValidFromValidTo, Find_or_Create_by_Name_On):
    
    email = Column(String(80), nullable=False)
    password = Column(String(80))
        
    @property
    def permissions(self):
        return _M2MCollection_(self,Permission,PersonPermission)


class PersonPermission(Base, ValidFromValidTo):
    
    from_ref = Column(Integer)
    to_ref = Column(Integer)
    
