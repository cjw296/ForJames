'''
Created on Nov 10, 2012

@author: peterb
'''
from sqlalchemy.ext.declarative import declarative_base, declared_attr,\
    has_inherited_table
import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.orm.deprecated_interfaces import SessionExtension
from sqlalchemy.orm import attributes
from sqlalchemy.orm.session import make_transient


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


class Find_or_Create_by_Name(object):
    
    @classmethod
    def find_or_create(cls, session, name, **kwargs):
        result = session.query(cls).filter_by(name=name).first()
        if result is None:
            result = cls(name=name, **kwargs)
            session.add(result)
        return result


class Reference(Base, Common, Find_or_Create_by_Name):
    
    id = Column(Integer, primary_key=True)
    name = Column(String(length=80))
    ref = Column(Integer, default=0)
    
    @classmethod
    def next_ref(cls, session, name):
        ref = cls.find_or_create(session, name, ref=0)
        ref.ref = ref.ref+1
        return ref.ref
                

class ValidFromValidTo(Common):
    
    id = Column('id',Integer, primary_key=True)
    ref = Column(Integer, index=True)
    valid_from = Column(DateTime(), default=datetime.datetime.now)
    valid_to = Column(DateTime(), default=None)

    @classmethod
    def valid_on(cls,on_date=None):
        if on_date is None:
            on_date=datetime.datetime.now()
        return and_(cls.valid_from <= on_date,
                    or_(cls.valid_to > on_date,
                        cls.valid_to == None))
    

    def new_version(self, session):
        # make us transient (removes persistent
        # identity). 
        make_transient(self)
        old_version = session.query(self.__class__).get(self.id)
        self.valid_from = datetime.datetime.now()
        old_version.valid_to = self.valid_from

        # set 'id' to None.  
        # a new PK will be generated on INSERT.
        self.id = None
    
    
class VersionExtension(SessionExtension):
    def before_flush(self, session, flush_context, instances):
        for instance in session.dirty:
            if not isinstance(instance, ValidFromValidTo):
                continue
            if not session.is_modified(instance, passive=True):
                continue

            if not attributes.instance_state(instance).has_identity:
                continue

            # make it transient
            if instance.valid_to is None:
                instance.new_version(session)
                # re-add
                session.add(instance)

    
    def after_attach(self, session, instance):  
        if isinstance(instance, ValidFromValidTo):
            instance.ref = Reference.next_ref(session, instance.__class__.__name__)

            