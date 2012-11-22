'''
Created on Nov 22, 2012

@author: peterb
'''

from tornado import web
from simple_colour.plumbing.access.access_handler import AccessHandler


class IndexHandler(web.RequestHandler):
    ''' Returns our index.html from templates folder '''
    
    def initialize(self, page='index.html'):
        self.page = page

    def get_current_user(self):
        return AccessHandler.get_auth_user_from_cookie(self)

    @web.authenticated    
    def get(self):
        self.render(self.page)
