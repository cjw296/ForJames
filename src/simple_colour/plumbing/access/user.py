'''
Created on Nov 12, 2012

@author: peterb
'''
import json


class User(object):
    '''
        Represents an authenticated user.
    '''
    
    def __init__(self, id, email, permissions):
        self.id = id
        self.email = email
        self.permissions = permissions

    def has_permissions(self, *args):
        for arg in args:
            if arg in self.permissions:
                return True
        return False
    
    def to_json(self):
        return json.dumps({"id":self.id, "email": self.email, "permissions": self.permissions})

