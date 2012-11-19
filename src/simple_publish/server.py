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

define("port", 8080, type=int, help="server port number (default: 8080)")
define("db_url", 'sqlite:///simple_publish_vfvt.db', help="sqlalchemy db url")


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


class PageEditHandler(tornado.web.RequestHandler):
    
    tmpl = "page-edit-tmpl.html"
    
    def get(self, ref, *args, **kwargs):
        session = self.application.Session()
        try:
            page = None
            pages = list(model.Page.query(session).order_by(model.Page.sequence).all())
            if ref:
                page = model.Page.by_ref(session, ref)
            else:
                page = pages[0]
            self.render(self.tmpl, 
                        page=page, 
                        pages=pages, 
                        error=kwargs.get("error"), 
                        action=kwargs.get("action"))
        finally:
            session.close()


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
                time.sleep(0.1)
                model.Publication.publish(session)
                session.commit()
        finally:
            session.close()
        

def main():
    tornado.options.parse_command_line()
    application = Application([
        (r"/", MainHandler),
        (r"/page/(.*)/edit.html", PageEditHandler),
        (r"/page/(.*)", PageHandler),
    ], static_path=resource_filename("web","www/static"), 
       template_path=resource_filename("simple_publish","templates"),
       debug=True)
    application.listen(options.port)
    logging.info('listening on port %s', options.port)
    tornado.ioloop.IOLoop.instance().start()
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()