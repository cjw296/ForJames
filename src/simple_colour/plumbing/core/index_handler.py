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

    def get(self):  
        if self.application.settings.get('login_url') and self.current_user is None:
            raise web.HTTPError(403)
        self.render(self.page)
