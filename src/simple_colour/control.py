'''
Created on Nov 22, 2012

@author: peterb
'''
from simple_colour import model
from simple_colour import plumbing
import logging

class Control(plumbing.AccessControl):
    ''' Wraps a connection to the model, marshaling information to and from it via a session '''
    
    def colours(self):
        ''' returns the current list of colours and their votes '''
        
        with self._session_context as session:
            result = session.query(model.Colour.id, 
                                   model.Colour.name,
                                   model.Vote.votes).\
                             outerjoin(model.Vote,model.Colour.id==model.Vote.colour_id).\
                             order_by(model.Colour.name)
            return result.all()
            
            
    @plumbing.requires_permission(["admin"])
    def add_colour(self, colour_name):
        ''' adds a colour and broadcasts if new '''
        
        with self._session_context as session:
            colour = model.Colour.find_or_create(session, colour_name)
            if colour.id is None:
                session.commit()
                self._broadcast_on_success_("colour added",id=colour.id,
                                                           name=colour_name,
                                                           votes=0)
            else:
                logging.info("already there: %s", colour_name)
            
    
    def vote(self, colour_name):
        ''' votes for a colour (adding it if it does not exist) '''
        with self._session_context as session:
            vote = model.Vote.vote(session, colour_name)
            session.commit()
            self._broadcast_on_success_("voted", id=vote.colour.id,
                                                 name=vote.colour.name, 
                                                 votes=vote.votes)
        
        
            