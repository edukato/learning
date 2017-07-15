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
    phone_num = db.Column(db.Integer, unique=True)
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
    groups_list = db.Column(db.String)
    subjects = db.Column(db.String)
    mentor = db.Column(db.Integer)
    selling_log = db.relationship('SellingLog', backref='client',
                                  lazy='dynamic')
    events = db.relationship('Event', backref='client',
                             lazy='dynamic')
    grades = db.relationship('Grade', backref='client',
                             lazy='dynamic')
    road_maps = db.relationship('RoadMap', backref='client',
                               lazy='dynamic')
    answers = db.relationship('Answer', backref='client',
                              lazy='dynamic')
    schedules = db.relationship('Schedule', backref='client',
                                lazy='dynamic')
    skils = db.relationship('Skil', backref='client',
                                lazy='dynamic')
    training_recommendation_sessions = db.relationship('TrainingRecommendationSession', backref='client',
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

    def last_n_transactions(self, n):
        list_of_trans = SellingLog.query.filter(SellingLog.client_id == self.id).order_by(
            SellingLog.id.desc()).limit(n)
        for last_transaction in list_of_trans:
            last_transaction.name = (Service.query.filter(Service.id == last_transaction.service_id).first()).name
        return list_of_trans

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
    grade = db.Column(db.Integer)

    def __repr__(self):
        return '<Grade: {}>'.format(self.id)


class SellingLog(db.Model):

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
    details = db.Column(db.String(300))
    type = db.Column(db.Integer)
    transaction_id = db.Column(db.Integer, db.ForeignKey('selling_log.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    image = db.Column(db.String(300))

    def __repr__(self):
        return '<Event: {}>'.format(self.id)


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.Integer)
    institution = db.Column(db.String)
    course = db.Column(db.Integer)
    achievements = db.Column(db.String)
    grades = db.relationship('Grade', backref='teacher',
                             lazy='dynamic')
    events = db.relationship('Event', backref='teacher',
                             lazy='dynamic')
    salaries = db.relationship('Salary', backref='teacher',
                               lazy='dynamic')
    schedules = db.relationship('Schedule', backref='teacher',
                                lazy='dynamic')
    operating_schedules = db.relationship('OperatingSchedules', backref='teacher',
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
    price = db.Column(db.Integer)
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

class RoadMap(db.Model):
    __tablename__ = 'road_maps'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    step = db.Column(db.Integer)
    name = db.Column(db.String(300))
    description = db.Column(db.String(300))
    if_done = db.Column(db.Boolean)

    def __repr__(self):
        return '<RoadMap: {}>'.format(self.id)


class ONews(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    link = db.Column(db.String(300))
    text = db.Column(db.String)
    image = db.Column(db.String)
    video = db.Column(db.String)
    document = db.Column(db.String)
    audio = db.Column(db.String)

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


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    solution = db.Column(db.String)
    number = db.Column(db.Integer)
    text = db.Column(db.String)
    image = db.Column(db.String)
    right_answer = db.Column(db.String)
    answers = db.relationship('Answer', backref='task',
                              lazy='dynamic')
    tasks_errors = db.relationship('TasksError', backref='task',
                              lazy='dynamic')

    def __repr__(self):
        return '<Task: {}>'.format(self.id)


class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    answer = db.Column(db.String)
    right = db.Column(db.Boolean)
    training_type = db.Column(db.Integer)
    training_id = db.Column(db.Integer)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    task_number = db.Column(db.Integer)

    def __repr__(self):
        return '<Answer: {}>'.format(self.id)

class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    time = db.Column(db.DateTime)
    if_done = db.Column(db.Boolean)
    interval_number = db.Column(db.Integer)

    def __repr__(self):
        return '<Schedule: {}>'.format(self.id)

class TrainingChoice(db.Model):
    __tablename__ = 'training_choices'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    number = db.Column(db.Integer)
    description = db.Column(db.String)

    def __repr__(self):
        return '<Training_choice: {}>'.format(self.id)

class Skil(db.Model):
    __tablename__ = 'skils'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    subject = db.Column(db.String)
    number = db.Column(db.Integer)
    level = db.Column(db.Integer)

    def __repr__(self):
        return '<Skil: {}>'.format(self.id)

class TrainingRecommendationSession(db.Model):
    __tablename__ = 'training_recommendation_sessions'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    subject = db.Column(db.String)
    start_date = db.Column(db.DateTime)
    if_close = db.Column(db.Boolean)
    current_question = db.Column(db.Integer)
    questions = db.Column(db.String)
    answers = db.Column(db.String)

    def __repr__(self):
        return '<TrainingRecommendationSession: {}>'.format(self.id)

class TasksError(db.Model):
    __tablename__ = 'tasks_errors'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    error = db.Column(db.String)

    def __repr__(self):
        return '<TasksError: {}>'.format(self.id)

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String)
    description = db.Column(db.String)
    tasks_number = db.Column(db.Integer)
    answers = db.relationship('Answer', backref='subject',
                            lazy='dynamic')
    tasks = db.relationship('Task', backref='subject',
                            lazy='dynamic')
    schedules = db.relationship('Schedule', backref='subject',
                                          lazy='dynamic')
    operating_schedules = db.relationship('OperatingSchedules', backref='subject',
                            lazy='dynamic')

    def __repr__(self):
        return '<Subject: {}>'.format(self.id)

class OperatingSchedules(db.Model):
    __tablename__ = 'operating_schedules'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    day_of_the_week = db.Column(db.Integer)
    interval_number = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<OperatingSchedules: {}>'.format(self.id)