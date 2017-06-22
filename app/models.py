# app/models.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class Client(UserMixin, db.Model):
    """
    Create an User table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    middle = db.Column(db.String(60), index=True)
    email = db.Column(db.String(60), index=True, unique=True)
    phone_num = db.Column(db.Integer, unique = True)
    social_network = db.Column(db.String(60))
    status = db.Column(db.Integer)
    description = db.Column(db.String(300))
    date_of_reg = db.Column(db.DateTime)
    password_hash = db.Column(db.String(128))
<<<<<<< HEAD

=======
>>>>>>> c7885f74a49672cab7a9b2bd163734265bdec856

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Client: {}>'.format(self.id)


# Set up user_loader
@login_manager.user_loader
def load_client(client_id):
    return Client.query.get(int(client_id))


class Grade(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.relationship('Client', backref='grade',
                                lazy='dynamic')
    teacher_id = db.relationship('Teacher', backref='grade',
                                 lazy='dynamic')
    control_work = db.Column(db.String(200))
    description = db.Column(db.String(200))
    picrel = db.Column(db.String(200))
    grade = db.Column (db.Integer)

    def __repr__(self):
        return '<Grade: {}>'.format(self.id)


class SellingLog(db.Model):
    """
    Create a Role table
    """

    __tablename__ = 'selling_log'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.relationship('Client', backref='sellinglog',
                                lazy='dynamic')
    service_id = db.relationship('Service', backref='sellinglog',
                                lazy='dynamic')
    amount = db.Column(db.Integer)
    price = db.Column(db.Integer)
    dicount = db.Column(db.Integer)


    def __repr__(self):
        return '<SellingLog: {}>'.format(self.id)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.relationship('Client', backref='event',
                                lazy='dynamic')
    service_id = db.relationship('Service', backref='event',
                                lazy='dynamic')
    date_time = db.Column(db.DateTime)
    details = db.Column(db.String (300))
    type = db.Column(db.Integer)
    transaction_id = db.relationship ('SellingLog', backref = "event",
                                     lazy = 'dynamic')
    teacher_id = db.relationship('Teacher', backref='event',
                                  lazy='dynamic')

    def __repr__(self):
        return '<Event: {}>'.format(self.id)


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60))
    last_name = db.Column(db.String(60))
    middle = db.Column(db.String(60))
    email = db.Column(db.String(60))
    phone_num = db.Column(db.Integer)
    description = db.Column(db.String(300))

    def __repr__(self):
        return '<Teacher: {}>'.format(self.id)

class Service(db.Model):
    __tablename__ = 'list_of_services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    description = db.Column(db.String(300))
    start_date = db.Column(db.DateTime)
    expiration_date = db.Column(db.DateTime)
    price = db.Column (db.Integer)

    def __repr__(self):
        return '<Service: {}>'.format(self.id)

class Salary(db.Model):
    __tablename__ = 'salary'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.relationship('Teacher', backref='salary',
                                 lazy='dynamic')
    date = db.Column(db.DateTime)
    description = db.Column(db.String(300))

    def __repr__(self):
        return '<Salary: {}>'.format(self.id)
