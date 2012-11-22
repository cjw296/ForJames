'''
Created on Nov 22, 2012

@author: peterb
'''
import tornado.web
from simple_colour.plumbing.core.control import Control
from simple_colour.plumbing.access.access_handler import AccessHandler

class ApplJsHandler(tornado.web.RequestHandler):
    ''' 
        A self describing Control expresses as a tornado template, 
        sent back as javascript
    '''
    def get_current_user(self):
        return AccessHandler.get_auth_user_from_cookie(self)

    @tornado.web.authenticated
    def get(self):
        self.add_header("content-type", "text/javascript")
        self.render("appl.js", description=Control._describe_service_(Control.CONTROL))
        
