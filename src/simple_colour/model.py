'''
Created on Nov 22, 2012

@author: peterb
'''
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from simple_colour.plumbing import Base, Common


class Colour(Base, Common):
    
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    
    @classmethod
    def find_or_create(cls, session, name):
        result = session.query(cls).filter(cls.name==name).first()
        if result is None:
            result = cls(name=name)
            session.add(result)
        return result
    

class Vote(Base, Common):
    
    id = Column(Integer, primary_key=True)
    votes = Column(Integer, default=0)
    colour_id = Column(Integer, ForeignKey('colour.id'))
    colour = relationship('Colour')
    
    @classmethod
    def vote(cls, session, name):
        result = session.query(Colour.id, cls).\
                                  outerjoin(cls, Colour.id==cls.colour_id).\
                                  filter(Colour.name==name).\
                                  first()
        colour_id, vote = result if result else (None,None)
        if colour_id is None:
            colour = Colour(name=name)
            vote = cls(colour=colour, votes=0)
            session.add_all([colour, vote])
        if vote is None:
            vote = cls(colour_id=colour_id, votes=0)
            session.add(vote)
        vote.votes = vote.votes + 1
        return vote
        
