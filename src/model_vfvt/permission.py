'''
Created on Nov 18, 2012

@author: peterb
'''

from sqlalchemy.types import String
from sqlalchemy.schema import Column
from model_vfvt.base import Base,ValidFromValidTo
from sqlalchemy.sql.expression import and_
import datetime

ADMIN_ROLE = u'admin'
USER_ROLE = u'user'
DEV_ROLE = u'dev'
AUTOMATIC_ROLE = 'automatic'
REMOTE_ROLE = "remote"

class Permission(Base, ValidFromValidTo):
    
    ROLES = [ADMIN_ROLE, USER_ROLE, DEV_ROLE, AUTOMATIC_ROLE, REMOTE_ROLE]

    name = Column(String(80), nullable=False)
    