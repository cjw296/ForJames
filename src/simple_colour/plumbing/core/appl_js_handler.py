'''
Created on Nov 22, 2012

@author: peterb
'''
from tornado import web
from simple_colour.plumbing.core.control import Control
from simple_colour.plumbing.access.access_handler import AccessHandler

class ApplJsHandler(web.RequestHandler):
    ''' 
        A self describing Control expresses as a tornado template, 
        sent back as javascript
    '''
    def get_current_user(self):
        return AccessHandler.get_auth_user_from_cookie(self)

    def get(self):
        if self.application.settings.get('login_url') and self.current_user is None:
            raise web.HTTPError(403)
        self.add_header("content-type", "text/javascript")
        self.render("plumbing/appl.js", description=Control._describe_service_(Control.CONTROL))
        
