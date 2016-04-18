from flask.ext.login import UserMixin, AnonymousUserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class DBStoredValue(db.Model):
    name = db.Column(db.String(), unique=True, primary_key=True)
    val = db.Column(db.String())

    def __init__(self, key, value):
        self.name = str(key)
        self.val = str(value)

    def __repr__(self):
        return '<DBStoredValue {0}: {1}>'.format(self.name, self.val)

    def get_key(self):
        return self.name

    def get_value(self):
        return self.val


class EmailEntry(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    address = db.Column(db.String())
    validity = db.Column(db.Boolean())
    processed = db.Column(db.Boolean())
    spam = db.Column(db.Boolean())

    def __init__(self, address):
        self.address = address

    def __repr__(self):
        if self.validity:
            result = '<EmailEntry %s (valid)>' % self.address
        else:
            result = '<EmailEntry %s (invalid)>' % self.address

        return result

    def set_validity(self, value):
        self.validity = bool(value)

    def is_vaild(self):
        return self.validity

    def set_processed(self, value):
        self.processed = bool(value)

    def is_processed(self):
        return self.processed

    def set_spam(self, value):
        self.spam = bool(value)

    def has_spam(self):
        return self.spam

    def get_address(self):
        return self.address


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.username
