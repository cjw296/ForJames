'''
The idea here was to create a model without version and then build a model
with valid_from valid_to so that we can see what the data looked like
at any particular time. This then allows us to have a publishing date
and leave the view fixed at that date but continue to edit the data.

Then publishing is changing the view date. If we mess up, just go back to
the old date....

Note that this model is slow - but we will have pages in memory.

if works the same with model or model_vfvt

Created on Nov 17, 2012

@author: peterb
'''
from pkg_resources import resource_filename
from tornado.options import options, define
import tornado.options
import tornado.ioloop
import tornado.web

import model_vfvt as model
import logging
import time
from sqlalchemy.sql.expression import and_

define("port", 8080, type=int, help="server port number (default: 8080)")
define("db_url", 'sqlite:///simple_publish_vfvt.db', help="sqlalchemy db url")

COOKIE_NAME = "simple_publish_session"

class AccessHandler(tornado.web.RequestHandler):
    '''
        Given a GET of no action Then renders login.html.
        Given a GET with action logout Then clear cookie and redirect to /.
        Given a POST will authenticate email, password with control and set cookie and redirect to next_url.
    '''
    
    def get(self, error=None):
        if self.get_argument("action", None) == 'logout':
            self.clear_cookie(COOKIE_NAME)
            self.redirect('/')
            return
        email = self.get_argument("email",default=None)
        self.render("login.html", email=email, error=error)
        
                
    def post(self):
        session = self.application.Session()
        try:
            email = self.get_argument("email")
            password = self.get_argument("password")
            person = model.Person.query(session).filter(and_(model.Person.email==email,
                                                             model.Person.password==password)).first()
            if person is None:
                raise Exception("Email or password incorrect!")
            
            self.set_secure_cookie(COOKIE_NAME, str(person.ref))
            
            next_url = self.get_argument('next', '/')
            self.redirect(next_url)
        except Exception, ex:
            self.get(error=str(ex))
        finally:
            session.close()
            
    @classmethod
    def get_auth_user_from_cookie(cls, handler):
        return handler.get_secure_cookie(COOKIE_NAME)
            

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("/page/")
        
class PageHandler(tornado.web.RequestHandler):
    
    tmpl = "page-tmpl.html"
    
    def get(self, label, *args):
        session = self.application.Session()
        try:
            on_date = model.Publication.publication_date(session)
            page = None
            pages = list(model.Page.query(session, on_date).order_by(model.Page.sequence).all())
            if label:
                for item in pages:
                    if item.label == label:
                        page = item
                        break
            else:
                page = pages[0]
            self.render(self.tmpl, page=page, pages=pages, on_date=on_date)
        finally:
            session.close()


class UserEditHandler(tornado.web.RequestHandler):
    
    tmpl = "users-edit-tmpl.html"
    
    def get_current_user(self):
        return AccessHandler.get_auth_user_from_cookie(self)
    
    
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        session = self.application.Session()
        try:
            people = list(model.Person.query(session).all())
            permissions = list(model.Permission.query(session).all())
            self.render(self.tmpl, 
                        page_name='users',
                        people=people, 
                        permissions=permissions, 
                        error=kwargs.get("error"), 
                        action=kwargs.get("action"))
        finally:
            session.close()
            
            
class PageEditHandler(tornado.web.RequestHandler):
    
    tmpl = "page-edit-tmpl.html"
    
    def get_current_user(self):
        return AccessHandler.get_auth_user_from_cookie(self)
    
    
    @tornado.web.authenticated
    def get(self, ref, *args, **kwargs):
        session = self.application.Session()
        try:
            page = None
            pages = list(model.Page.query(session).order_by(model.Page.sequence).all())
            if ref and ref != '-':
                page = model.Page.by_ref(session, ref)
            else:
                self.redirect("/page/%s/edit-html" % pages[0].ref)
            self.render(self.tmpl,
                        page_name='pages', 
                        page=page, 
                        pages=pages, 
                        error=kwargs.get("error"), 
                        action=kwargs.get("action"))
        finally:
            session.close()


    @tornado.web.authenticated
    def post(self, ref, *args):
        error = None
        session = self.application.Session()
        try:
            action = self.get_argument("submit")
            if action == "Create":
                page = model.Page(title=self.get_argument('title'),
                                  content=self.get_argument('content'))
                session.add(page)
                session.commit()
                ref = page.ref
                
            elif action == "Save":
                page = model.Page.by_ref(session, ref)
                page.title = self.get_argument('title')
                page.content = self.get_argument('content')
                session.commit()
                
            elif action == "Delete":
                if session.query(model.Page).count() == 1:
                    raise Exception("Cannot delete last page!")
                page = model.Page.by_ref(session, ref)
                session.delete(page)
                session.commit()
                
            elif action == "Add":
                page = model.Page.by_ref(session, ref)
                page.tags.append(model.Tag.find_or_create(session, self.get_argument("tag")))
                session.commit()
                
            elif action == "Remove":
                page = model.Page.by_ref(session, ref)
                for tag_id in self.get_arguments("remove_tag_id"):
                    tag = model.Tag.by_ref(session, tag_id)
                    page.tags.remove(tag)
                session.commit()
                
            elif action == "Publish":
                model.Publication.publish(session)
                session.commit()
            
            elif action == "Save Order":
                sequence = [int(i) for i in self.get_argument('page_order').split(',')]
                for i,sequence_ref in enumerate(sequence):
                    model.Page.by_ref(session, sequence_ref).sequence=i
                session.commit()
                
        except Exception,ex:
            error = str(ex)
        finally:
            session.close()
            
        if error is None and action=="Create":
            self.redirect("/page/%s/edit-html" % ref)
        elif error is None and action=="Delete":
            page = session.query(model.Page).first()
            self.redirect("/page/%s/edit-html" % page.ref)
        elif error is None and action=="Publish":
            self.redirect("/page/")
        else:
            self.get(ref, *args, error=error, action=action)
        

class Application(tornado.web.Application):
    
    def __init__(self, *args, **kwargs):
        tornado.web.Application.__init__(self, *args, **kwargs)
        self.Session, self.engine = model.create_initialize_db(options.db_url)
        session = self.Session()
        try:
            page = model.Page.query(session).first()
            if page is None:
                session.add(model.Page(title="Index",content="Sample Page."))
                session.commit()
                time.sleep(0.2)
                model.Publication.publish(session)
                session.commit()
        finally:
            session.close()
        

def main():
    tornado.options.parse_command_line()
    application = Application([
        (r"/", MainHandler),
        (r"/login", AccessHandler),
        (r"/page/(.*)/edit.html", PageEditHandler),
        (r"/page/(.*)", PageHandler),
        (r"/users", UserEditHandler),
    ], static_path=resource_filename("web","www/static"), 
       template_path=resource_filename("simple_publish","templates"),
       cookie_secret="it_was_a_dark_and_stormy_night_for_publishing",
       login_url="/login",
       debug=True)
    application.listen(options.port)
    logging.info('listening on port %s', options.port)
    tornado.ioloop.IOLoop.instance().start()
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()