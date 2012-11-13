'''
Created on Nov 10, 2012

@author: peterb
'''

from sqlalchemy.types import Integer, String
from sqlalchemy.schema import Column
from model.base import Base

ADMIN_ROLE = u'admin'
USER_ROLE = u'user'
DEV_ROLE = u'dev'
AUTOMATIC_ROLE = 'automatic'
REMOTE_ROLE = "remote"


class Permission(Base):
    __tablename__ = "permission"
    
    ROLES = [ADMIN_ROLE, USER_ROLE, DEV_ROLE, AUTOMATIC_ROLE, REMOTE_ROLE]

    id = Column(Integer, primary_key=True)
    name =  Column(String(80), nullable=False, unique=True)
    
    @classmethod
    def find_or_create(cls, session, name):
        result = session.query(cls).filter(cls.name==name).first()
        if result is None:
            result = cls(name=name)
            session.add(result)
            session.flush()
        return result