'''
This is from: http://docs.sqlalchemy.org/en/rel_0_7/orm/tutorial.html#

Just select web.py and choose 'Run As / Python Run' from the Run menu.

Then read the console and the code...

Created on Nov 13, 2012

@author: peterb
'''
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
import logging

''' get an instance of Base to subclass for you model classes '''
Base = declarative_base()

class User(Base):
    '''
        model class to represent user
    '''
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)



def run():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    session = Session()
    try:
        ed_user = User('ed', 'Ed Jones', 'edspassword')
        session.add(ed_user)
        session.commit()
        
        our_user = session.query(User).filter_by(name='ed').first()
        logging.info("is ed in the db: %s",ed_user is our_user)
    finally:
        session.close()
        
        
        
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    run()