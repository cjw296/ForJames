'''
Created on Nov 10, 2012

@author: peterb
'''
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
    
    
    @classmethod
    def by_ref(cls, session, id, on_date=None):
        return session.query(cls).get(id)
    
    @classmethod
    def query(cls, session, on_date=None):
        return session.query(cls)

    @property
    def ref(self):
        return self.id