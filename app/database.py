from app import app, db_configs
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_configs.user}:{db_configs.password}@{db_configs.host}:{db_configs.port}/{db_configs.database}'
db = SQLAlchemy(app)


class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    token_jwt = db.Column(db.String())
    
    def __repr__(self):
        return '<Auth %d>' % self.id


class Home(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    configuration = db.Column(db.String(50))
    
    def __repr__(self):
        return '<Home %d>' % self.id


users_devices = db.Table('users_devices',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('device_id', db.Integer, db.ForeignKey('device.id'), primary_key=True)
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    date_nasc = db.Column(db.Date())
    devices = db.relationship('Device', secondary=users_devices, lazy='subquery',
        cascade='all,delete', backref=db.backref('users', lazy=True))

    def columns(self):
        return {
            column.name: getattr(self, column.name, None)
            for column in self.__table__.columns
        }
    
    def __repr__(self):
        return '<User %d>' % self.id


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alias_name = db.Column(db.String(50), nullable=False)
    serie_number = db.Column(db.String(50), unique=True, nullable=False)
    firmware_version = db.Column(db.String(20))
    device_type = db.Column(db.Integer, db.ForeignKey('device_type.id'))

    def columns(self):
        return {
            column.name: getattr(self, column.name, None)
            for column in self.__table__.columns
        }

    def __repr__(self):
        return '<Device %r>' % self.username


class DeviceType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)

    def columns(self):
        return {
            column.name: getattr(self, column.name, None)
            for column in self.__table__.columns
        }

    def __repr__(self):
        return '<DeviceType %r>' % self.username


class DeviceField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    field_type = db.Column(db.String(20), nullable=False)
    device_type = db.Column(db.Integer, db.ForeignKey('device_type.id'), nullable=False)

    def columns(self):
        return {
            column.name: getattr(self, column.name, None)
            for column in self.__table__.columns
        }

    def __repr__(self):
        return '<DeviceField %r>' % self.username


class DeviceAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    action_type = db.Column(db.String(20), nullable=False)
    device_type = db.Column(db.Integer, db.ForeignKey('device_type.id'), nullable=False)

    def columns(self):
        return {
            column.name: getattr(self, column.name, None)
            for column in self.__table__.columns
        }

    def __repr__(self):
        return '<DeviceAction %r>' % self.username


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hour = db.Column(db.Integer)
    minute = db.Column(db.Integer)
    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime())
    active = db.Column(db.Boolean)
    slot = db.Column(db.Integer)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)

    def columns(self):
        return {
            column.name: getattr(self, column.name, None)
            for column in self.__table__.columns
        }
    
    def __repr__(self):
        return '<Config %d>' % self.id


class Alarm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    minutes = db.Column(db.Integer)
    hours = db.Column(db.Integer)
    repeatitions = db.Column(db.Integer)
    repeatitions_interval = db.Column(db.Integer)
    light = db.Column(db.Boolean)
    light_duration = db.Column(db.Integer)
    sound = db.Column(db.Boolean)
    sound_duration = db.Column(db.Integer)
    inform_to_user = db.Column(db.Boolean)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    
    def __repr__(self):
        return '<Alarm %d>' % self.id