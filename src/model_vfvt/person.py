'''
Created on Nov 18, 2012

@author: peterb
'''

from sqlalchemy.types import String, Integer
from sqlalchemy.schema import Column
from model_vfvt.base import Base,ValidFromValidTo, Find_or_Create_by_Name_On
from sqlalchemy.orm.session import object_session
from sqlalchemy.sql.expression import and_
import datetime

from model_vfvt.permission import Permission

class Person(Base, ValidFromValidTo, Find_or_Create_by_Name_On):
    
    email = Column(String(80), nullable=False)
    password = Column(String(80))
    
    ''' Permision support '''
    def add_permission(self, permission):
        if self.ref is None or permission.ref is None:
            raise Exception("Add to relation on versioned object before adding to session")
        session = object_session(self)
        session.add(PersonPermission(person_ref=self.ref, 
                                     permission_ref=permission.ref))
            
    def remove_permission(self, permission, on_date=None):
        if self.ref is None or permission.ref is None:
            raise Exception("Remove from relation on versioned object before adding to session")
        session = object_session(self)
        perperm = session.query(PersonPermission.permission_ref).filter(and_(PersonPermission.person_ref==self.ref,
                                                                             PersonPermission.permission_ref==permission.ref,
                                                                             PersonPermission.valid_on())).first()
        if perperm is not None:
            perperm.valid_to = on_date if on_date is not None else datetime.datetime.now()
    
    @property
    def permissions(self):
        session = object_session(self)
        subselect = session.query(PersonPermission.permission_ref).filter(and_(PersonPermission.person_ref==self.ref,
                                                                               PersonPermission.valid_on()))
        query = session.query(Permission).filter(and_(Permission.ref.in_(subselect),
                                                      Permission.valid_on()))
        return query


class PersonPermission(Base, ValidFromValidTo):
    
    person_ref = Column(Integer)
    permission_ref = Column(Integer)
    
