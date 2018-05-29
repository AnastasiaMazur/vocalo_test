from app import db


class HubspotToken(db.Document):
    access_token = db.StringField()
    refresh_token = db.StringField()


class User(db.Document):
    email = db.EmailField()
    hub_domain = db.StringField(max_length=150)
    token = db.ReferenceField('HubspotToken')


class Deal(db.Document):
    deal_id = db.IntField(required=True)
    name = db.StringField(required=True, max_length=150)
    source = db.StringField(required=True, max_length=150)
    close_date = db.DateTimeField(required=True)
    user = db.ReferenceField('User')

