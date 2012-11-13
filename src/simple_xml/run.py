'''
This uses the common model package.

Just select web.py and choose 'Run As / Python Run' from the Run menu.

Then read the console and the code...

Created on Nov 13, 2012

@author: peterb
'''
import xml.etree.ElementTree as ET
import model
import logging

def run(db_url="sqlite://", xml_path="people.xml"):
    Session,engine = model.create_initialize_db(db_url, echo=True)
    session = Session()
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for child in root:
            if child.tag == "person":
                email = child.find("email").text
                permissions_list = child.find("permissions").text.split(',')
                person = model.Person(email=email)
                session.add(person)
                for name in permissions_list:
                    person.permissions.append(model.Permission.find_or_create(session, name))
        session.commit()
        for person in session.query(model.Person).all():
            print person
    finally:
        session.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    run()