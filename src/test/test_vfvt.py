'''
Created on Nov 18, 2012

@author: peterb
'''
import unittest
import model_vfvt as model
import time


class Test(unittest.TestCase):


    def setUp(self):
        self._Session, self._engine = model.create_initialize_db("sqlite://", echo=False)
        self.session = self._Session()


    def tearDown(self):
        self.session.close()
        self._engine.dispose()
        self._Session = self._engine = None


    def testTag(self):
        tag = model.Tag(name='foo')
        self.session.add(tag)
        self.session.commit()
        time.sleep(0.5)
        tag.name = 'harry'
        self.session.commit()
            
        print '------------ tag 1'
        
        for tag in self.session.query(model.Tag):
            print tag.id, tag.ref, tag.name, tag.valid_from, tag.valid_to
            
        print '------------ tag 2'
        
        for tag in self.session.query(model.Tag).filter(model.Tag.valid_on()):
            print tag.id, tag.ref, tag.name, tag.valid_from, tag.valid_to


    def testPage(self):
        tag = model.Tag(name='bar')
        page = model.Page(title='foo')
        self.session.add_all([page,tag])
        page.add_tag(tag)
        self.session.commit()
            
        print '------------ page'
        
        for page in self.session.query(model.Page).filter(model.Page.valid_on()):
            print page.id, page.ref, page.title, page.valid_from, page.valid_to
            for tag in page.tags:
                print '\t', tag.id, tag.ref, tag.name, tag.valid_from, tag.valid_to


    def testOwner(self):
        tag = model.Tag(name='bar')
        page = model.Page(title='foo')
        person = model.Person(email="spddo@me.com")
        self.session.add_all([page, tag, person])
        page.add_tag(tag)
        page.owner = person
        self.session.commit()
            
        print '------------ owner'
        
        for page in self.session.query(model.Page).filter(model.Page.valid_on()):
            print page.id, page.ref, page.title, page.valid_from, page.valid_to, page.owner_ref
            owner = page.owner
            if owner:
                print '\t', owner.id, owner.ref, owner.email, owner.valid_from, owner.valid_to

        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()