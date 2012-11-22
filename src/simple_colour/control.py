'''
Created on Nov 22, 2012

@author: peterb
'''
from simple_colour import model
from simple_colour.plumbing import SessionControl
import logging

class Control(SessionControl):
        
    def colours(self):
        ''' returns the current list of colours and their votes '''
        
        with self.session as session:
            result = session.query(model.Colour.id, 
                                   model.Colour.name,
                                   model.Vote.votes).\
                             outerjoin(model.Vote,model.Colour.id==model.Vote.colour_id).\
                             order_by(model.Colour.name)
            return result.all()
            
            
    def add_colour(self, colour_name):
        ''' adds a colour and broadcasts if new '''
        
        with self.session as session:
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
        with self.session as session:
            vote = model.Vote.vote(session, colour_name)
            session.commit()
            self._broadcast_on_success_("voted", id=vote.colour.id,
                                                 name=vote.colour.name, 
                                                 votes=vote.votes)
        
        
            