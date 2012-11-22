'''
Created on Nov 22, 2012

@author: peterb
'''
from sqlalchemy.types import Integer, String
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr,\
    has_inherited_table



Base = declarative_base()


class Common(object):
    
    @declared_attr
    def __tablename__(self):
        if (has_inherited_table(self) and
            Common not in self.__bases__):
            return None
        return self.__name__.lower()
    
    
    @declared_attr
    def __table_args__(self):
        return { 'mysql_engine':'InnoDB' }
    


class Person(Base, Common):
    
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


ADMIN_ROLE = u'admin'
USER_ROLE = u'user'


class Permission(Base, Common):
    
    ROLES = [ADMIN_ROLE, USER_ROLE]

    id = Column(Integer, primary_key=True)
    name =  Column(String(80), nullable=False, unique=True)
    
    @classmethod
    def find_or_create(cls, session, name):
        result = session.query(cls).filter(cls.name==name).first()
        if result is None:
            result = cls(name=name)
            session.add(result)
        return result
    