# Importando as bibliotecas necessárias
import os
from flask_mail import Mail
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from models import User, db

# Criação da aplicação Flask
app = Flask(__name__)

# Configuração da aplicação
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Caminho do banco de dados
app.config['SECRET_KEY'] = 'setordeinteligenciamelhor'  # Chave secreta para a sessão
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')  # Pasta de upload
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Servidor de e-mail
app.config['MAIL_PORT'] = 587  # Porta do servidor de e-mail
app.config['MAIL_USERNAME'] = 'sysggoldensat@gmail.com'  # Nome de usuário do e-mail
app.config['MAIL_PASSWORD'] = 'yzxs ieko subp xesu'  # Senha do e-mail
app.config['MAIL_USE_TLS'] = True  # Uso de TLS
app.config['MAIL_USE_SSL'] = False  # Uso de SSL
app.config['MAIL_DEFAULT_SENDER'] = 'gikesaj434@dxice.com'  # Remetente padrão do e-mail

# Criação do objeto Mail
mail = Mail(app)

# Inicialização do SQLAlchemy
db.init_app(app)

# Criação do objeto Migrate
migrate = Migrate(app, db)

# Criação do objeto LoginManager
login_manager = LoginManager()
login_manager.init_app(app)  # Inicialização do LoginManager
login_manager.login_view = 'login'  # Definição da view de login

# Função para carregar o usuário
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Retorna o usuário pelo ID

@app.cli.command("promote_to_admin")
def promote_to_admin():
    email = input("Enter the email of the user to promote: ")
    user = User.query.filter_by(email=email).first()
    if user is None:
        print(f'No user found with email {email}')
    else:
        user.access_level = 'Admin'
        db.session.commit()
        print(f'User {email} has been promoted to Admin')

# Importação das rotas
from routes import *

# Execução da aplicação
if __name__ == '__main__':
        app.run(debug=True)
        # app.run(host='0.0.0.0', port=5051)  # Executa a aplicação no host 0.0.0.0 e na porta 5051
