# app.py
import os
from flask_mail import Mail
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from models import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'setordeinteligenciamelhor'
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'sysggoldensat@gmail.com'
app.config['MAIL_PASSWORD'] = 'yzxs ieko subp xesu'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'gikesaj434@dxice.com'  # Remetente padrão para e-mails enviados pela aplicação

mail = Mail(app)

db = SQLAlchemy()
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
        db.create_all() 
        app.run(debug=True)
        # app.run(host='0.0.0.0', port=5050)
