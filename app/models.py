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
    phone_num = db.Column(db.String(60), unique=True)
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
    plan = db.Column(db.Integer)
    groups_list = db.Column(db.String(300))
    subjects = db.Column(db.String(300))
    mentor = db.Column(db.Integer)
    chat_bot_1 = db.Column(db.Boolean)
    chat_bot_2 = db.Column(db.Boolean)
    chat_bot_3 = db.Column(db.Boolean)
    chat_bot_4 = db.Column(db.Boolean)
    chat_bot_5 = db.Column(db.Boolean)
    chat_bot_6 = db.Column(db.Boolean)
    loboda_date = db.Column(db.DateTime)
    step_number = db.Column(db.Integer)
    wish_list = db.Column(db.String(300))
    pre_ege_res = db.Column(db.String(300))
    interesting_subjects = db.Column(db.String(300))
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
    mentors_claims = db.relationship('MentorsClaim', backref='client',
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
    lessons = db.Column(db.Integer)
    consultations = db.Column(db.Integer)
    lessons_now = db.Column(db.Integer)
    consultations_now = db.Column(db.Integer)

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
    institution = db.Column(db.String(300))
    course = db.Column(db.Integer)
    achievements = db.Column(db.String(300))
    want_be_mentor = db.Column(db.Boolean)
    skype_login = db.Column(db.String(300))

    materials = db.relationship('Material', backref='teacher',
                             lazy='dynamic')
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
    mentors_claims = db.relationship('MentorsClaim', backref='teacher',
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
    full_description = db.Column(db.String(300))
    reviews = db.Column(db.String(300))
    video = db.Column(db.String(300))
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
    amount = db.Column(db.Integer)

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


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    solution = db.Column(db.String())
    number = db.Column(db.Integer)
    text = db.Column(db.String(350))
    image = db.Column(db.String(300))
    right_answer = db.Column(db.String(300))
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
    answer = db.Column(db.String(300))
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
    description = db.Column(db.String(300))

    def __repr__(self):
        return '<Training_choice: {}>'.format(self.id)

class Skil(db.Model):
    __tablename__ = 'skils'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    subject = db.Column(db.String(300))
    number = db.Column(db.Integer)
    level = db.Column(db.Integer)
    right_percent = db.Column(db.Float)
    answers_amount = db.Column(db.Integer)

    def __repr__(self):
        return '<Skil: {}>'.format(self.id)

class TrainingRecommendationSession(db.Model):
    __tablename__ = 'training_recommendation_sessions'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    subject = db.Column(db.String(300))
    start_date = db.Column(db.DateTime)
    if_close = db.Column(db.Boolean)
    current_question = db.Column(db.Integer)
    questions = db.Column(db.String(300))
    answers = db.Column(db.String(300))

    def __repr__(self):
        return '<TrainingRecommendationSession: {}>'.format(self.id)

class TasksError(db.Model):
    __tablename__ = 'tasks_errors'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    error = db.Column(db.String(300))

    def __repr__(self):
        return '<TasksError: {}>'.format(self.id)

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(300))
    description = db.Column(db.String(300))
    tasks_number = db.Column(db.Integer)
    icon = db.Column(db.String(300))
    materials = db.relationship('Material', backref='subject',
                              lazy='dynamic')
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

class MentorsClaim(db.Model):
    __tablename__ = 'mentors_claims'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    claim = db.Column(db.String(300))

    def __repr__(self):
        return '<MentorsClaim: {}>'.format(self.id)

class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    date = db.Column(db.DateTime)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    title = db.Column(db.String(300))
    description = db.Column(db.String(300))
    text = db.Column(db.String(300))

    def __repr__(self):
        return '<Material: {}>'.format(self.id)