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
    balance = db.Column(db.Integer)
    year_of_study = db.Column(db.Integer)
    birth_date = db.Column(db.Date)
    school = db.Column(db.String(300))
    home_address = db.Column(db.String(300))
    image = db.Column(db.String(300))
    plan = db.Column(db.String(300))
    selling_log = db.relationship('SellingLog', backref='client',
                               lazy='dynamic')
    events = db.relationship('Event', backref='client',
                               lazy='dynamic')
    grades = db.relationship('Grade', backref='client',
                               lazy='dynamic')

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
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
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
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('list_of_services.id'))
    amount = db.Column(db.Integer)
    price = db.Column(db.Integer)
    dicount = db.Column(db.Integer)
    date_time = db.Column(db.DateTime)
    access_start = db.Column(db.DateTime)
    access_end = db.Column(db.DateTime)
    image = db.Column(db.String(300))

    def __repr__(self):
        return '<SellingLog: {}>'.format(self.id)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('list_of_services.id'))
    date_time = db.Column(db.DateTime)
    details = db.Column(db.String (300))
    type = db.Column(db.Integer)
    transaction_id = db.Column(db.Integer, db.ForeignKey('selling_log.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    image = db.Column(db.String(300))

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
    image = db.Column(db.String(300))
    grades = db.relationship('Grade', backref='teacher',
                               lazy='dynamic')
    events = db.relationship('Event', backref='teacher',
                               lazy='dynamic')
    salaries = db.relationship('Salary', backref='teacher',
                               lazy='dynamic')

    def __repr__(self):
        return '<Teacher: {}>'.format(self.first_name)


class Service(db.Model):
    __tablename__ = 'list_of_services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    description = db.Column(db.String(300))
    start_date = db.Column(db.DateTime)
    expiration_date = db.Column(db.DateTime)
    price = db.Column (db.Integer)
    image = db.Column(db.String(300))
    type = db.Column(db.Integer)
    selling_log = db.relationship('SellingLog', backref='service',
                               lazy='dynamic')
    events = db.relationship('Event', backref='service',
                               lazy='dynamic')

    def __repr__(self):
        return '<Service: {}>'.format(self.id)


class Salary(db.Model):
    __tablename__ = 'salaries'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    date = db.Column(db.DateTime)
    description = db.Column(db.String(300))

    def __repr__(self):
        return '<Salary: {}>'.format(self.id)

class RouteMap(db.Model):
    __tablename__ = 'route_maps'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    transaction_id = db.Column(db.Integer, db.ForeignKey('selling_log.id'))
    step = db.Column(db.Integer)
    name = db.Column(db.String(300))
    description = db.Column(db.String(300))
    if_done = db.Column(db.Binary)

    def __repr__(self):
        return '<RouteMap: {}>'.format(self.id)

class ONews(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    link = db.Column(db.String(300))
    text = db.Column(db.String(300))
    image = db.Column(db.String(300))
    video = db.Column(db.String(300))
    document = db.Column(db.String(300))
    audio = db.Column(db.String(300))

    def __repr__(self):
        return '<Onews: {}>'.format(self.id)

class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    link = db.Column(db.String(300))
    news = db.relationship('ONews', backref='group',
                             lazy='dynamic')

    def __repr__(self):
        return '<Group: {}>'.format(self.id)
