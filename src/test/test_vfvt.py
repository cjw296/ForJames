'''
Created on Nov 18, 2012

@author: peterb
'''
import unittest
from model_vfvt import create_initialize_db, Person, Tag, Page
import time


class Test(unittest.TestCase):


    def setUp(self):
        self._Session, self._engine = create_initialize_db("sqlite://", echo=False)
        self.session = self._Session()


    def tearDown(self):
        self.session.close()
        self._engine.dispose()
        self._Session = self._engine = None
        
    
    def test_person(self):
            
        print '------------ person'
        
        for person in self.session.query(Person).filter(Person.valid_on()):
            print person.id, person.ref, person.email, person.valid_from, person.valid_to
            for perm in person.permissions:
                print '\t', perm.id, perm.ref, perm.name, perm.valid_from, perm.valid_to


    def testTag(self):
        tag = Tag.find_or_create(self.session,'foo')
        self.session.commit()
        time.sleep(0.5)
        tag.name = 'harry'
        self.session.commit()
            
        print '------------ tag 1'
        
        for tag in self.session.query(Tag):
            print tag.id, tag.ref, tag.name, tag.valid_from, tag.valid_to
            
        print '------------ tag 2'
        
        for tag in self.session.query(Tag).filter(Tag.valid_on()):
            print tag.id, tag.ref, tag.name, tag.valid_from, tag.valid_to


    def testPage(self):
        tag = Tag.find_or_create(self.session,'bar')
        page = Page(title='foo')
        self.session.add(page)
        page.tags.append(tag)
        self.session.commit()
            
        print '------------ page'
        
        for page in self.session.query(Page).filter(Page.valid_on()):
            print page.id, page.ref, page.title, page.valid_from, page.valid_to
            for tag in page.tags:
                print '\t', tag.id, tag.ref, tag.name, tag.valid_from, tag.valid_to


    def testOwner(self):
        tag = Tag(name='bar')
        page = Page(title='foo')
        person = Person(email="spddo@me.com")
        self.session.add_all([page, tag, person])
        page.tags.append(tag)
        page.owner = person
        self.session.commit()
        self.session.expire_all()
            
        print '------------ owner'
        
        for page in self.session.query(Page).filter(Page.valid_on()):
            print page.id, page.ref, page.title, page.valid_from, page.valid_to, page.owner_ref
            owner = page.owner
            if owner:
                print '\t', owner.id, owner.ref, owner.email, owner.valid_from, owner.valid_to
        
        page.owner = None
        self.session.commit()
        self.session.expire_all()
        
        for page in self.session.query(Page).filter(Page.valid_on()):
            print page.id, page.ref, page.title, page.valid_from, page.valid_to, page.owner_ref
            owner = page.owner
            if owner:
                print '\t', owner.id, owner.ref, owner.email, owner.valid_from, owner.valid_to

        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()