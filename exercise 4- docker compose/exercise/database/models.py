from .db import db


class ResearchGroup(db.Document):
    name = db.StringField(required=True)
    description = db.StringField()
    founder = db.ReferenceField('Professor', required= True, dbref=False)

class Professor(db.Document):
    name = db.StringField(required=True)
    designation = db.StringField(required=True, choices=('Professor', 'Assistant Professor', 'Associate Professor'))
    email = db.StringField()
    interests = db.ListField(db.StringField())
    researchGroups = db.ListField(db.ReferenceField('ResearchGroup', dbref=False))
    

class Student(db.Document):
    name = db.StringField(required=True)
    studentNumber = db.StringField(required=True)
    researchGroups = db.ListField(db.ReferenceField('ResearchGroup', dbref=False))
