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
from sqlalchemy.orm.session import make_transient, object_session


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
        query = session.query(cls).filter_by(name=name)
        result = query.first()
        if result is None:
            result = cls(name=name, **kwargs)
            session.add(result)
        return result
    

class Find_or_Create_by_Name_On(object):
    
    @classmethod
    def find_or_create(cls, session, name, on_date=None):
        if on_date is None:
            on_date = datetime.datetime.now()
        result = session.query(cls).filter(and_(cls.name==name,
                                                cls.valid_on(on_date=on_date))).first()
        if result is None:
            ''' check to see there is not one in the future '''
            next_one = session.query(cls).filter(and_(cls.name==name,
                                                      cls.valid_from > on_date)).first()
            if next_one:
                on_date = next_one.valid_from
            result = cls(name=name, valid_from=on_date)
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
    
    
    @classmethod
    def by_ref(cls, session, ref, on_date=None):
        return session.query(cls).filter(and_(cls.ref==ref, cls.valid_on(on_date))).first()
    
    @classmethod
    def query(cls, session, on_date=None):
        return session.query(cls).filter(cls.valid_on(on_date))
    
    @classmethod
    def valid_on(cls,on_date=None):
        if on_date is None:
            on_date=datetime.datetime.now()
        return and_(cls.valid_from <= on_date,
                    or_(cls.valid_to > on_date,
                        cls.valid_to == None))
        
    
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
        if isinstance(instance, ValidFromValidTo) and instance.ref is None:
            instance.ref = Reference.next_ref(session, instance.__class__.__name__)


class _M2MCollection_():
    
    def __init__(self, item, related_cls, relation_cls):
        self.item = item
        self.session = object_session(item)
        self.related_cls = related_cls
        self.relation_cls = relation_cls
        
    
    def __iter__(self):
        subselect = self.session.query(self.relation_cls.to_ref).filter(and_(self.relation_cls.from_ref==self.item.ref,
                                                                              self.relation_cls.valid_on()))
        query = self.session.query(self.related_cls).filter(and_(self.related_cls.ref.in_(subselect),
                                                                 self.related_cls.valid_on()))
        return iter(query)
    
    
    ''' Tag support '''
    def append(self, obj, on_date=None):
        if self.item.ref is None or obj.ref is None:
            raise Exception("Add to relation on versioned object before adding to session")
        if on_date is None:
            on_date = datetime.datetime.now()
        self.session.add(self.relation_cls(from_ref=self.item.ref, to_ref=obj.ref, valid_from=on_date))
            
            
    def remove(self, obj, on_date=None):
        if self.item.ref is None or obj.ref is None:
            raise Exception("Remove from relation on versioned object before adding to session")
        if on_date is None:
            on_date = datetime.datetime.now()
        result = self.session.query(self.relation_cls).filter(and_(self.relation_cls.from_ref==self.item.ref,
                                                                   self.relation_cls.to_ref==obj.ref,
                                                                   self.relation_cls.valid_on())).first()
        if result is not None:
            result.valid_to = on_date
