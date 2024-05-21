# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from pytz import timezone
import pytz

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_picture = db.Column(db.String(100), default='/img/logo-golden.png')
    additional_info = db.Column(db.Text)
    access_level = db.Column(db.String(20), default='User')
    unread_notifications = db.Column(db.Integer, default=0)  # Contador de notificações não lidas

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
fuso_horario_brasilia = timezone('America/Sao_Paulo')

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(120), nullable=False)
    reason = db.Column(db.String(20), nullable=False)
    billing = db.Column(db.String(20), nullable=False)
    model = db.Column(db.String(120), nullable=False)
    customization = db.Column(db.String(120), nullable=False)
    equipment_number = db.Column(db.String(20), nullable=False)
    problem_type = db.Column(db.String(50), nullable=False)
    photos = db.Column(db.String(255), nullable=True)
    treatment = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pendente')
    date_completed = db.Column(db.String(20), nullable=True, default=lambda: datetime.now(tz=fuso_horario_brasilia).strftime('%d/%m/%Y %H:%M'))
    image_paths = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"Report('{self.title}')"
    
class SalesRequest(db.Model):
    __tablename__ = 'sales_request'

    id = db.Column(db.Integer, primary_key=True)
    date_completed = db.Column(db.String(20), nullable=True, default=lambda: datetime.now(tz=fuso_horario_brasilia).strftime('%d/%m/%Y %H:%M'))
    cnpj = db.Column(db.String(20))
    contract_start = db.Column(db.String(20))
    vigency = db.Column(db.String(20))
    reason = db.Column(db.String(50))
    location = db.Column(db.String(50), default='n/a')
    maintenance_number = db.Column(db.String(100), default='n/a')
    client = db.Column(db.String(120))
    sales_rep = db.Column(db.String(50))
    contract_type = db.Column(db.String(50))
    shipping = db.Column(db.String(50))
    delivery_fee = db.Column(db.Float, default='n/a')
    address = db.Column(db.String(200))
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    model = db.Column(db.String(50))
    customization = db.Column(db.String(100))
    tp = db.Column(db.String(50))
    charger = db.Column(db.String(100))
    cable = db.Column(db.String(100))
    invoice_type = db.Column(db.String(50))
    value = db.Column(db.String(50))
    total_value = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    observations = db.Column(db.Text)
    accept_terms = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), nullable=False, default='Pendente')
    date_sent_to_customer = db.Column(db.String(20), nullable=True)
    equipment_numbers = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"SalesRequest('{self.client}')"
    
class Log(db.Model):
    __tablename__ = 'log'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.String(20), nullable=True, default=lambda: datetime.now(tz=fuso_horario_brasilia).strftime('%d/%m/%Y %H:%M'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('logs', lazy=True))

    def __repr__(self):
        return f"Log('{self.action}', '{self.timestamp}', '{self.user_id}')"

class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))
    type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False ,index=True, default=datetime.now(pytz.timezone('America/Sao_Paulo')))
    viewed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<Notification {self.id}>"
    
class Entrance(db.Model):
    __tablename__ = 'entrance'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=True, default=lambda: datetime.now(tz=fuso_horario_brasilia).strftime('%d/%m/%Y %H:%M'))
    client = db.Column(db.String(120), nullable=False)
    entrance_type = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50))
    customization = db.Column(db.String(100))
    type_of_receipt = db.Column(db.String(50), nullable=False)
    recipients_name = db.Column(db.String(50), default= 'n/a')
    withdrawn_by = db.Column(db.String(50), default= 'n/a')
    equipment_numbers = db.Column(db.String(200), nullable=False)
    maintenance_status = db.Column(db.String(50), default='Pendente')
    returned_equipment_numbers = db.Column(db.String(200))
    accept_terms = db.Column(db.Boolean, default=False)

class Reactivation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=True, default=lambda: datetime.now(tz=fuso_horario_brasilia).strftime('%d/%m/%Y %H:%M'))
    client = db.Column(db.String(120), nullable=False)
    reactivation_reason = db.Column(db.String(120), nullable=False)
    request_channel = db.Column(db.String(90), nullable=False)
    equipments = db.relationship('Equipment', backref='reactivation', lazy=True)
    value = db.Column(db.String(50), nullable=False)
    total_value = db.Column(db.String(50), nullable=False)
    observation = db.Column(db.Text)

    def __repr__(self):
        return f'<Reactivation {self.nome_cliente}>'
    
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reactivation_id = db.Column(db.Integer, db.ForeignKey('reactivation.id'), nullable=False)
    equipment_id = db.Column(db.String(100), nullable=False)
    equipment_ccid = db.Column(db.String(100), nullable=False)