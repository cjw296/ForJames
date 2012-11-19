'''
Created on Nov 19, 2012

@author: peterb
'''
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, DateTime

from model_vfvt import Base
from model_vfvt.base import Common
import datetime
from sqlalchemy.sql.expression import func


class Publication(Base, Common):
    
    id = Column(Integer, primary_key=True)
    on_date = Column(DateTime)

    
    @classmethod
    def publish(cls, session, on_date=None):
        if on_date is None:
            on_date = datetime.datetime.now()
        result = cls(on_date=on_date)
        session.add(result)
        return result
    
    @classmethod
    def publication_date(cls, session):
        return session.query(func.MAX(cls.on_date)).first()[0]