from flask.ext.mongoengine import MongoEngine

from .utils import random_alphanum

from time import time

db = MongoEngine()

EXPIRES_DELTA = 300


class User(db.Document):
    login = db.StringField(required=True)
    passwd_hash = db.StringField(required=True)

    # consumers the user is subscribed to
    consumers = db.ListField(db.ObjectIdField('Consumer'))

    # consumers the user has created
    owned_consumers = db.ListField(db.ObjectIdField('Consumer'))

    def check_password(self, password):
        return db.app.bcrypt.check_password_hash(self.passwd_hash, password)

    def set_password(self, password):
        self.passwd_hash = db.app.bcrypt.generate_password_hash(password)


class Consumer(db.Document):
    name = db.StringField(required=True)
    key = db.StringField(required=True)
    secret = db.StringField(required=True)
    callback_uri = db.StringField()
    last_timestamp = db.IntField(default=0)

    # a list of previous nonces and timestamps hashed together
    previous_requests = db.ListField(db.StringField())

    def save(self, *args, **kwargs):
        if self.key is None:
            self.key = random_alphanum(32)
            self.secret = random_alphanum(32)

        db.Document.save(self, *args, **kwargs)


class TokenMixin(db.Document):
    oauth_token = db.StringField(required=True)
    oauth_token_secret = db.StringField(required=True)
    ctime = db.IntField(required=True)

    def save(self, *args, **kwargs):
        if self.oauth_token is None:
            self.oauth_token = random_alphanum(32)
            self.oauth_token_secret = random_alphanum(32)
            self.ctime = time()

            if hasattr(self, 'expires'):
                self.expires = time() + EXPIRES_DELTA

        db.Document.save(self, *args, **kwargs)


class RequestToken(TokenMixin):
    meta = {'allow_inheritance': True}

    oauth_callback = db.StringField()
    oauth_verifier = db.StringField()
    expires = db.IntField(required=True)

    def is_expired(self):
        return time() > self.expires


class AccessToken(TokenMixin):
    meta = {'allow_inheritance': True}

    user_id = db.ObjectIdField(required=True)
    consumer_id = db.ObjectIdField(required=True)
