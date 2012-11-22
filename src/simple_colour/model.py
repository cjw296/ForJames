'''
Created on Nov 22, 2012

@author: peterb
'''
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class Colour(Base):
    __tablename__ = "colour"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    
    
    @classmethod
    def find_or_create(cls, session, name):
        result = session.query(cls).filter(cls.name==name).first()
        if result is None:
            result = cls(name=name)
            session.add(result)
        return result
    

class Vote(Base):
    __tablename__ = "vote"
    
    id = Column(Integer, primary_key=True)
    votes = Column(Integer, default=0)
    
    colour_id = Column(Integer, ForeignKey('colour.id'))
    colour = relationship('Colour')
    
    @classmethod
    def vote(cls, session, name):
        colour = Colour.find_or_create(session, name)
        if colour.id is None:
            vote = cls(colour=colour,votes=1) 
            session.add(vote)
        else:
            vote = session.query(cls).filter(cls.colour_id==colour.id).first()
            if vote is None:
                vote = cls(colour=colour,votes=1) 
                session.add(vote)
            else:
                vote.votes = vote.votes + 1
        return vote
        
