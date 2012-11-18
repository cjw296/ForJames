'''
Created on Nov 18, 2012

@author: peterb
'''

from sqlalchemy.types import Integer, String
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.orm import relationship
from model.base import Base

class Tag(Base):
    __tablename__ = "tag"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

    ''' one to many relation ''' 
    parent_id = Column(Integer, ForeignKey('tag.id'))
    parent = relationship('Tag', 
                         remote_side='tag.c.id', 
                         backref="children")
    
    pages = relationship('Page', secondary="page_tag", back_populates="tags")

    
    def __init__(self, name):
        '''so you can construct as Tag('foo') rather than Tag(name-'foo') '''
        self.name = name

    def __repr__(self):
        return "<Tag name=%r>" % self.name
    
    @classmethod
    def find_or_create_all(cls, session, names):
        result = session.query(cls).filter(cls.name.in_(names)).all()
        missing_names = set(names) - set([e.name for e in result])
        for name in missing_names:
            tag = cls(name)
            session.add(tag)
            result.append(tag)
        return result
    
    @classmethod
    def find_or_create(cls, session, name):
        result = session.query(cls).filter(cls.name==name).first()
        if result is None:
            result = cls(name)
            session.add(result)
        return result
    
        
page_tag = Table('page_tag', Base.metadata,
    Column('page_id', Integer, ForeignKey('page.id')),
    Column('tag_id', Integer, ForeignKey('tag.id')),
    mysql_engine='InnoDB'
)
