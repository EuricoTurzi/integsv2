# Importando as bibliotecas necessárias
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, Numeric
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from pytz import timezone
import pytz

# Criação do objeto SQLAlchemy
db = SQLAlchemy()

# Definição da classe User, que herda de UserMixin e db.Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Nome da tabela no banco de dados

    # Definição das colunas da tabela
    id = db.Column(db.Integer, primary_key=True)  # ID do usuário
    username = db.Column(db.String(100), unique=True, nullable=False)  # Nome de usuário
    email = db.Column(db.String(100), unique=True, nullable=False)  # E-mail do usuário
    password_hash = db.Column(db.String(128), nullable=False)  # Hash da senha do usuário
    profile_picture = db.Column(db.String(100), default='logo-golden.png')  # Imagem de perfil do usuário
    additional_info = db.Column(db.Text)  # Informações adicionais sobre o usuário
    access_level = db.Column(db.String(20), default='User')  # Nível de acesso do usuário

    # Método para definir a senha do usuário
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)  # Gera o hash da senha e armazena na coluna password_hash

    # Método para verificar a senha do usuário
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  # Verifica se o hash da senha fornecida corresponde ao hash armazenado
    
fuso_horario_brasilia = timezone('America/Sao_Paulo')

# Definição da classe Report, que herda de db.Model
class Report(db.Model):
    __tablename__ = 'reports'  # Nome da tabela no banco de dados

    # Definição das colunas da tabela
    id = db.Column(db.Integer, primary_key=True)  # ID do relatório
    client_name = db.Column(db.String(120), nullable=False)  # Nome do cliente
    reason = db.Column(db.String(20), nullable=False)  # Motivo do relatório
    billing = db.Column(db.String(20), nullable=False)  # Faturamento
    model = db.Column(db.String(120), nullable=False)  # Modelo do equipamento
    customization = db.Column(db.String(120), nullable=False)  # Personalização do equipamento
    equipment_number = db.Column(db.String(20), nullable=False)  # Número do equipamento
    problem_type = db.Column(db.String(50), nullable=False)  # Tipo de problema
    photos = db.Column(db.String(255), nullable=True)  # Fotos do problema
    treatment = db.Column(db.String(50), nullable=False)  # Tratamento do problema
    status = db.Column(db.String(20), nullable=False, default='Pendente')  # Status do relatório
    date_completed = db.Column(db.String(20), nullable=True, default=lambda: datetime.now(tz=fuso_horario_brasilia).strftime('%d/%m/%Y %H:%M'))  # Data de conclusão do relatório
    image_paths = db.Column(db.Text, nullable=True)  # Caminhos das imagens do relatório

    # Método para representar o objeto como uma string
    def __repr__(self):
        return f"Report('{self.title}')"
    
# Definição da classe SalesRequest, que herda de db.Model
class SalesRequest(db.Model):
    __tablename__ = 'sales_request'  # Nome da tabela no banco de dados

    # Definição das colunas da tabela
    id = db.Column(db.Integer, primary_key=True)  # ID da requisição de venda
    date_completed = db.Column(db.String(20), nullable=True, default=lambda: datetime.now(tz=fuso_horario_brasilia).strftime('%d/%m/%Y %H:%M'))  # Data de conclusão da requisição
    cnpj = db.Column(db.String(20))  # CNPJ do cliente
    contract_start = db.Column(db.String(20))  # Início do contrato
    vigency = db.Column(db.String(20))  # Vigência do contrato
    reason = db.Column(db.String(50))  # Motivo da requisição
    location = db.Column(db.String(50), default='n/a')  # Localização da requisição
    maintenance_number = db.Column(db.String(100), default='n/a')  # Número de manutenção
    client = db.Column(db.String(120))  # Nome do cliente
    sales_rep = db.Column(db.String(50))  # Representante de vendas
    contract_type = db.Column(db.String(50))  # Tipo de contrato
    shipping = db.Column(db.String(50))  # Método de envio
    delivery_fee = db.Column(Numeric(precision=16, scale=2))  # Taxa de entrega
    address = db.Column(db.String(200))  # Endereço de entrega
    contact_person = db.Column(db.String(100))  # Pessoa de contato
    email = db.Column(db.String(120))  # E-mail do cliente
    phone = db.Column(db.String(20))  # Telefone do cliente
    quantity = db.Column(db.Integer)  # Quantidade de equipamentos
    model = db.Column(db.String(50))  # Modelo do equipamento
    customization = db.Column(db.String(100))  # Personalização do equipamento
    tp = db.Column(db.String(50))  # Tipo de produto
    charger = db.Column(db.String(100))  # Carregador do equipamento
    cable = db.Column(db.String(100))  # Cabo do equipamento
    invoice_type = db.Column(db.String(50))  # Tipo de fatura
    value = db.Column(Numeric(precision=16, scale=2))  # Valor do equipamento
    total_value = db.Column(Numeric(precision=16, scale=2))  # Valor total da requisição
    payment_method = db.Column(db.String(50))  # Método de pagamento
    observations = db.Column(db.Text)  # Observações sobre a requisição
    accept_terms = db.Column(db.Boolean, default=False)  # Aceitação dos termos
    status = db.Column(db.String(20), nullable=False, default='Pendente')  # Status da requisição
    date_sent_to_customer = db.Column(db.String(20), nullable=True)  # Data de envio ao cliente
    equipment_numbers = db.Column(db.String(200), nullable=True)  # Números dos equipamentos

    # Método para representar o objeto como uma string
    def __repr__(self):
        return f"SalesRequest('{self.client}')"
    
# Definição da classe Log, que herda de db.Model
class Log(db.Model):
    __tablename__ = 'log'  # Nome da tabela no banco de dados

    # Definição das colunas da tabela
    id = db.Column(db.Integer, primary_key=True)  # ID do log
    action = db.Column(db.String(255), nullable=False)  # Ação registrada no log
    timestamp = db.Column(db.String(20), nullable=True, default=lambda: datetime.now(tz=fuso_horario_brasilia).strftime('%d/%m/%Y %H:%M'))  # Data e hora do log
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ID do usuário associado ao log
    
    # Definição da relação entre as tabelas User e Log
    user = db.relationship('User', backref=db.backref('logs', lazy=True))  # Relação com a tabela User

    # Método para representar o objeto como uma string
    def __repr__(self):
        return f"Log('{self.action}', '{self.timestamp}', '{self.user_id}')"
    
# Definição da classe Entrance, que herda de db.Model
class Entrance(db.Model):
    __tablename__ = 'entrance'  # Nome da tabela no banco de dados

    # Definição das colunas da tabela
    id = db.Column(db.Integer, primary_key=True)  # ID da entrada
    date = db.Column(db.String(20), nullable=True, default=lambda: datetime.now(tz=fuso_horario_brasilia).strftime('%d/%m/%Y %H:%M'))  # Data da entrada
    client = db.Column(db.String(120), nullable=False)  # Nome do cliente
    entrance_type = db.Column(db.String(50), nullable=False)  # Tipo de entrada
    model = db.Column(db.String(50))  # Modelo do equipamento
    customization = db.Column(db.String(100))  # Personalização do equipamento
    type_of_receipt = db.Column(db.String(50), nullable=False)  # Tipo de recibo
    recipients_name = db.Column(db.String(50), default= 'n/a')  # Nome do destinatário
    withdrawn_by = db.Column(db.String(50), default= 'n/a')  # Retirado por
    equipment_numbers = db.Column(db.String(200), nullable=False)  # Números dos equipamentos
    maintenance_status = db.Column(db.String(50), default='Pendente')  # Status da manutenção
    returned_equipment_numbers = db.Column(db.String(200))  # Números dos equipamentos retornados
    accept_terms = db.Column(db.Boolean, default=False)  # Aceitação dos termos

# Definição da classe Reactivation, que herda de db.Model
class Reactivation(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID da reativação
    date = db.Column(db.String(20), nullable=True, default=lambda: datetime.now(tz=fuso_horario_brasilia).strftime('%d/%m/%Y %H:%M'))  # Data da reativação
    client = db.Column(db.String(120), nullable=False)  # Nome do cliente
    reactivation_reason = db.Column(db.String(120), nullable=False)  # Motivo da reativação
    request_channel = db.Column(db.String(90), nullable=False)  # Canal de solicitação
    equipments = db.relationship('Equipment', backref='reactivation', lazy=True)  # Relação com a tabela Equipment
    value = db.Column(db.String(50), nullable=False)  # Valor da reativação
    total_value = db.Column(db.String(50), nullable=False)  # Valor total da reativação
    observation = db.Column(db.Text)  # Observações sobre a reativação

    # Método para representar o objeto como uma string
    def __repr__(self):
        return f'<Reactivation {self.nome_cliente}>'
    
# Definição da classe Equipment, que herda de db.Model
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID do equipamento
    reactivation_id = db.Column(db.Integer, db.ForeignKey('reactivation.id'), nullable=False)  # ID da reativação associada ao equipamento
    equipment_id = db.Column(db.String(100), nullable=False)  # ID do equipamento
    equipment_ccid = db.Column(db.String(100), nullable=False)  # CCID do equipamento

# Definição da classe EquipmentStock, que herda de db.Model
class EquipmentStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID do estoque de equipamentos
    model = db.Column(db.String(50))  # Modelo do equipamento
    quantity_in_stock = db.Column(db.Integer, default=0)  # Quantidade de equipamentos em estoque

# Definição da classe Provider, que herda de db.Model
class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID do prestador
    name = db.Column(db.String(50))  # Nome do prestador
    km_allowance = db.Column(db.Integer)  # Quilometragem permitida
    hour_allowance = db.Column(db.Time)  # Horas permitidas
    activation_value = db.Column(db.Float)  # Valor de ativação
    km_excess_value = db.Column(db.Float)  # Valor do excesso de quilometragem
    excess_value = db.Column(db.Float)  # Valor do excesso de horas

# Definição da classe Client, que herda de db.Model
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID do cliente
    name = db.Column(db.String(50))  # Nome do cliente
    km_allowance = db.Column(db.Integer)  # Quilometragem permitida
    hour_allowance = db.Column(db.Time)  # Horas permitidas
    activation_value = db.Column(db.Float)  # Valor de ativação
    km_excess_value = db.Column(db.Float)  # Valor do excesso de quilometragem
    excess_value = db.Column(db.Float)  # Valor do excesso de horas

# Definição da classe Activation, que herda de db.Model
class Activation(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID da ativação
    start_time = db.Column(db.DateTime)  # Data e hora de início da ativação
    end_time = db.Column(db.DateTime)  # Data e hora de término da ativação
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'))  # ID do prestador associado à ativação
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', name='fk_client_id'))  # ID do cliente associado à ativação
    plates = db.Column(db.String(50))  # Placas do veículo usado na ativação
    agents = db.Column(db.String(50))  # Agentes envolvidos na ativação
    equipment_id = db.Column(db.String(50))  # ID do equipamento usado na ativação
    initial_km = db.Column(db.Integer)  # Quilometragem inicial na ativação
    final_km = db.Column(db.Integer)  # Quilometragem final na ativação
    toll = db.Column(db.Float)  # Valor do pedágio na ativação
    client_toll = db.Column(db.Float)  # Valor do pedágio cobrado do cliente
    status = db.Column(db.String(20), default='Pendente')  # Status da ativação