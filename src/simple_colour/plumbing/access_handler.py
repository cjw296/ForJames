'''
Created on Nov 22, 2012

@author: peterb
'''
import tornado.web


class AccessHandler(tornado.web.RequestHandler):
    '''
        Given a GET of no action Then renders login.html.
        Given a GET with action logout Then clear cookie and redirect to /.
        Given a POST will authenticate email, password with control and set cookie and redirect to next_url.
    '''
    
    def get(self, error=None):
        if self.get_argument("action", None) == 'logout':
            self.clear_cookie(self.application.ACCESS_COOKIE_NAME)
            self.redirect('/')
            return
        email = self.get_argument("email",default=None)
        self.render("login.html", email=email, error=error)
        
                
    def post(self):
        try:
            email = self.get_argument("email")
            password = self.get_argument("password")
            accl_key = self.application.control._login_(email, password)
            self.set_secure_cookie(self.application.ACCESS_COOKIE_NAME, str(accl_key))
            
            next_url = self.get_argument('next', '/')
            self.redirect(next_url)
        except Exception, ex:
            self.get(error=str(ex))
            
    @classmethod
    def get_auth_user_from_cookie(cls, handler):
        return handler.get_secure_cookie(handler.application.ACCESS_COOKIE_NAME)