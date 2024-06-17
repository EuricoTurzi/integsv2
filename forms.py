# forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, ValidationError, SelectField, MultipleFileField,IntegerField, BooleanField, FormField, FieldList, Form, DecimalField, DateTimeField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, NumberRange

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ReportForm(FlaskForm):
    client_name = StringField('Nome do Cliente', validators=[DataRequired()])
    reason = SelectField('Motivo', choices=[('Manutenção', 'Manutenção'), ('Devolução/Estoque', 'Devolução/Estoque')], validators=[DataRequired()])
    billing = SelectField('Faturamento', choices=[('Com custo', 'Com custo'), ('Sem custo', 'Sem custo')], validators=[DataRequired()])
    model = StringField('Modelo', validators=[DataRequired()])
    customization = StringField('Customização', validators=[DataRequired()])
    equipment_number = StringField('Número do Equipamento', validators=[DataRequired()])
    problem_type = SelectField('Tipo de Problema', choices=[('Oxidação', 'Oxidação'), ('Placa danificada', 'Placa danificada'), ('Placa danificada sem custo', 'Placa danificada sem custo'), ('USB danificado', 'USB danificado'), ('USB danificado sem custo', 'USB danificado sem custo'), ('Botão de acionamento danificado', 'Botão de acionamento danificado'), ('Botão de acionamento danificado sem custo', 'Botão de acionamento danificado sem custo'), ('Antena LoRa danificada', 'Antena LoRa danificada'), ('Sem problemas identificados', 'Sem problemas identificados')], validators=[DataRequired()])
    photos = MultipleFileField('Fotos Anexadas', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens são permitidas.')])
    treatment = SelectField('Tratativa', choices=[('Oxidação', 'Oxidação'), ('Placa danificada', 'Placa danificada'), ('USB danificado', 'USB danificado'), ('Botão de acionamento danificado', 'Botão de acionamento danificado'), ('Antena LoRa danificada', 'Antena LoRa danificada'), ('Sem problemas identificados', 'Sem problemas identificados')], validators=[DataRequired()])
    submit = SubmitField('Salvar')

class ProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_picture = StringField('Foto de Perfil')
    additional_info = TextAreaField('Informações adicionais')
    submit = SubmitField('Save Changes')

class EditProfileForm(FlaskForm):
    description = TextAreaField('Descrição', validators=[DataRequired()])
    submit = SubmitField('Salvar Alterações')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')

    # Adicione este método para validar a senha atual
    def validate_current_password(self, field):
        if not current_user.check_password(field.data):
            raise ValidationError('Incorrect current password.')
        
class SalesRequestForm(FlaskForm):
    cnpj = StringField('CNPJ', validators=[DataRequired()])
    contract_start = StringField('Início de Contrato', validators=[DataRequired()])
    vigency = SelectField('Vigência', choices=[('N/A', 'N/A'), ('6 meses', '6 meses'), ('12 meses', '12 meses'), ('18 meses', '18 meses'), ('24 meses', '24 meses'), ('30 meses', '30 meses'), ('36 meses', '36 meses')], validators=[DataRequired()])
    reason = SelectField('Motivo', choices=[('Aquisição nova', 'Aquisição nova'), ('Manutenção', 'Manutenção'), ('Aditivo', 'Aditivo'),
                                            ('Extravio', 'Extravio'), ('Teste', 'Teste'), ('Isca Fast', 'Isca Fast'), ('Isca Fast - Agente', 'Isca Fast - Agente'), ('Antenista', 'Antenista'), ('Reversa', 'Reversa')], validators=[DataRequired()])
    maintenance_number = StringField('Protocolo de Manutenção', default='N/A', validators=[Optional()])
    location = StringField('Local de Saída', default='N/A', validators=[Optional()])
    client = StringField('Cliente', validators=[DataRequired()])
    sales_rep = SelectField('Comercial', choices=[('Aparecido', 'Aparecido'), ('Daniel', 'Daniel'), ('GoldenSat', 'GoldenSat'), ('Mayra', 'Mayra'),
                                                  ('Marcio', 'Marcio'), ('Penha', 'Penha'), ('Rubens', 'Rubens'),
                                                  ('Sheila', 'Sheila'), ('Thiago', 'Thiago')], validators=[DataRequired()])
    contract_type = SelectField('Contrato', choices=[('Retornável', 'Retornável'), ('Descartável', 'Descartável')], validators=[DataRequired()])
    shipping = SelectField('Envio', choices=[('Agente', 'Agente'), ('Retirada na base', 'Retirada na base'),
                                             ('Motoboy', 'Motoboy'), ('Transportadora', 'Transportadora'),
                                             ('Correio', 'Correio'), ('Comercial', 'Comercial')], validators=[DataRequired()])
    delivery_fee = DecimalField('Taxa de Entrega', validators=[Optional()])
    address = StringField('Endereço', validators=[DataRequired()])
    contact_person = StringField('A/C', validators=[DataRequired()])
    email = StringField('E-mail', validators=[Email()])
    phone = StringField('Telefone de Contato', validators=[DataRequired()])
    quantity = IntegerField('Quantidade', validators=[DataRequired()])
    model = SelectField('Modelo', choices=[('GS 410', 'GS 410'), ('GS 4410', 'GS 4410'), ('GS 419', 'GS 419'), ('GS 449', 'GS 449'), ('GS 33', 'GS 33'), ('GS 33 4G', 'GS 33 4G'),
                                           ('Tetis', 'Tetis'),('GS 480 (Antena)', 'GS 480 (Antena)'),('GS 489 (Antena)', 'GS 489 (Antena)'), ('Ayama (Antena)', 'Ayama (Antena)'), ('Tetis R', 'Tetis R'), ('GS Air', 'GS Air'), ('Lokies', 'Lokies'),
                                           ('Imobilizador GS340', 'Imobilizador GS340'),('Localizador GS310', 'Localizador GS310'),
                                           ('Localizador GS390', 'Localizador GS390'), ('Bodycam', 'Bodycam'), ('Carregador + Cabo', 'Carregador + Cabo')], validators=[DataRequired()])
    customization = SelectField('Customização', choices=[('Sem customização', 'Sem customização'),('Caixa de papelão', 'Caixa de papelão'),('Caixa de papelão (bateria desacoplada)','Caixa de papelão (bateria desacoplada)'),
                                                         ('Caixa de papelão + D.F', 'Caixa de papelão + D.F'), ('Termo branco', 'Termo branco'), ('Termo branco + imã', 'Termo branco + imã'),
                                                         ('Termo branco + D.F', 'Termo branco + D.F'), ('Termo branco slim', 'Termo branco slim'), ('Termo branco slim + D.F + ETQ', 'Termo branco slim + D.F + ETQ'),
                                                         ('Termo cinza slim + D.F + ETQ', 'Termo cinza slim + D.F + ETQ'), ('Termo branco slim (isopor)', 'Termo branco slim (isopor)'),
                                                         ('Termo branco - bateria externa', 'Termo branco - bateria externa'), ('Termo marrom + imã', 'Termo marrom + imã'),
                                                         ('Termo cinza', 'Termo cinza'),('Termo cinza + imã', 'Termo cinza + imã'),('Termo preto', 'Termo preto'),
                                                         ('Termo preto + imã', 'Termo preto + imã'), ('Termo branco | marrom - slim', 'Termo branco | marrom - slim'),
                                                         ('Termo marrom slim + D.F + ETQ', 'Termo marrom slim + D.F + ETQ'), ('Termo marrom', 'Termo marrom'),
                                                         ('Caixa blindada', 'Caixa blindada'), ('Tênis/sapato', 'Tênis/sapato'), ('Projetor', 'Projetor'),
                                                         ('Caixa de som', 'Caixa de som'), ('Luminária', 'Luminária'), ('Alexa', 'Alexa'), ('Videogame', 'Videogame'),
                                                         ('Secador de cabelo', 'Secador de cabelo'), ('Roteador', 'Roteador'), ('Relógio Digital', 'Relógio Digital')], validators=[DataRequired()])
    tp = StringField('TP', validators=[DataRequired()])
    charger = StringField('Carregador', validators=[DataRequired()])
    cable = StringField('Cabo', validators=[DataRequired()])
    invoice_type = SelectField('Tipo de Fatura', choices=[('Com custo', 'Com custo'), ('Sem custo', 'Sem custo')], validators=[DataRequired()])
    value = DecimalField('Valor Unitário', validators=[DataRequired()])
    total_value = DecimalField('Valor Total', validators=[DataRequired()])
    payment_method = StringField('Forma de Pagamento', validators=[DataRequired()])
    observations = TextAreaField('Observações', validators=[DataRequired()])
    accept_terms = BooleanField('Aceitar os ', validators=[DataRequired()])
    submit = SubmitField('Enviar Requisição')

    def __init__(self, *args, **kwargs):
        super(SalesRequestForm, self).__init__(*args, **kwargs)
        
        if 'reason' in kwargs and kwargs['reason'] not in ['Manutenção']:
            self.maintenance_number.data = 'N/A'
        if 'reason' in kwargs and kwargs['reason'] not in ['Isca Fast']:
            self.location.data = 'N/A'

class EntranceForm(FlaskForm):
    client = StringField('Cliente', validators=[DataRequired()])
    entrance_type = SelectField ('Tipo de Entrada', choices=[('Manutenção', 'Manutenção'), ('Devolução/Estoque', 'Devolução/Estoque') ], validators=[DataRequired()])
    model = SelectField('Modelo', choices=[('GS 410', 'GS 410'), ('GS 4410', 'GS 4410'), ('GS 419', 'GS 419'), ('GS 449', 'GS 449'), ('GS33', 'GS33'), ('GS33 4G', 'GS33 4G'),
                                           ('Tetis', 'Tetis'), ('Tetis R', 'Tetis R'), ('GSAir', 'GSAir'), ('Lokies', 'Lokies'),
                                           ('Imobilizador GS340', 'Imobilizador GS340'),('Localizador GS310', 'Localizador GS310'),
                                           ('Localizador GS390', 'Localizador GS390'), ('Bodycam', 'Bodycam')], validators=[DataRequired()])
    customization = SelectField('Customização', choices=[('Caixa de papelão', 'Caixa de papelão'),('Caixa de papelão (bateria desacoplada)','Caixa de papelão (bateria desacoplada)'),
                                                         ('Caixa de papelão + D.F', 'Caixa de papelão + D.F'), ('Termo branco', 'Termo branco'), ('Termo branco + imã', 'Termo branco + imã'),
                                                         ('Termo branco + D.F', 'Termo branco + D.F'), ('Termo branco slim', 'Termo branco slim'), ('Termo branco slim + D.F + ETQ', 'Termo branco slim + D.F + ETQ'),
                                                         ('Termo cinza slim + D.F + ETQ', 'Termo cinza slim + D.F + ETQ'), ('Termo branco slim (isopor)', 'Termo branco slim (isopor)'),
                                                         ('Termo branco - bateria externa', 'Termo branco - bateria externa'), ('Termo marrom + imã', 'Termo marrom + imã'),
                                                         ('Termo cinza', 'Termo cinza'),('Termo cinza + imã', 'Termo cinza + imã'),('Termo preto', 'Termo preto'),
                                                         ('Termo preto + imã', 'Termo preto + imã'), ('Termo branco | marrom - slim', 'Termo branco | marrom - slim'),
                                                         ('Termo marrom slim + D.F + ETQ', 'Termo marrom slim + D.F + ETQ'), ('Termo marrom', 'Termo marrom'),
                                                         ('Caixa blindada', 'Caixa blindada'), ('Tênis/sapato', 'Tênis/sapato'), ('Projetor', 'Projetor'),
                                                         ('Caixa de som', 'Caixa de som'), ('Luminária', 'Luminária'), ('Alexa', 'Alexa'), ('Videogame', 'Videogame'),
                                                         ('Secador de cabelo', 'Secador de cabelo'), ('Roteador', 'Roteador'), ('Relógio Digital', 'Relógio Digital')], validators=[DataRequired()])
    type_of_receipt = SelectField ('Recebimento', choices=[('Correios/Transportadora','Correios/Transportadora'), ('Entregue na base','Entregue na base'),('Retirado no cliente', 'Retirado no cliente')], validators=[DataRequired()])
    recipients_name = StringField ('Nome do Entregador', default='N/A', validators=[Optional()])
    withdrawn_by =  StringField ('Retirado por', default='N/A', validators=[Optional()])
    equipment_number = StringField('ID dos Equipamentos', validators=[DataRequired()])
    accept_terms = BooleanField('Aceitar os ', validators=[DataRequired()])

    def process_equipment_number(self):
        self.equipment_number.data = self.equipment_number.data.replace(' ', ';')

class EquipmentForm(Form):
    equipment_id = StringField('ID do Equipamento', validators=[DataRequired()])
    equipment_ccid = StringField('CCID do Equipamento', validators=[DataRequired()])

class ReactivationForm(FlaskForm):
    client = StringField('Nome do Cliente', validators=[DataRequired()])
    reactivation_reason = StringField('Motivo da Reativação', validators=[DataRequired()])
    request_channel = StringField('Canal de Solicitação', validators=[DataRequired()])
    equipments = FieldList(FormField(EquipmentForm), min_entries=1, max_entries=30)
    value = StringField('Valor Unitário', validators=[DataRequired()])
    total_value = StringField('Valor Total', validators=[DataRequired()]) 
    observation = TextAreaField('Observações')

class EquipmentStockForm(FlaskForm):
    model = SelectField('Modelo', choices=[('GS 410', 'GS 410'), ('GS 4410', 'GS 4410'), ('GS 419', 'GS 419'), ('GS 33', 'GS 33'), ('GS 33 4G', 'GS 33 4G'),
                                           ('Tetis', 'Tetis'),('GS 480 (Antena)', 'GS 480 (Antena)'),('GS 489 (Antena)', 'GS 489 (Antena)'), ('Ayama (Antena)', 'Ayama (Antena)'), ('Tetis R', 'Tetis R'), ('GS Air', 'GS Air'), ('Lokies', 'Lokies'),
                                           ('Imobilizador GS340', 'Imobilizador GS340'),('Localizador GS310', 'Localizador GS310'),
                                           ('Localizador GS390', 'Localizador GS390'), ('Bodycam', 'Bodycam'), ('ESEYE', 'ESEYE'), ('1NCE', '1NCE'), ('Carregador + Cabo', 'Carregador + Cabo')], validators=[DataRequired()])
    quantity_in_stock = IntegerField('Quantidade', validators=[DataRequired()])

class ActivationForm(FlaskForm):
    start_time = DateTimeField('Data e Hora Inicial', format='%d/%m/%Y %H:%M', validators=[DataRequired()])
    end_time = DateTimeField('Data e Hora Final', format='%d/%m/%Y %H:%M', validators=[Optional()])
    provider = SelectField('Prestador', coerce=int)
    plates = StringField('Placas', validators=[DataRequired()])
    agents = StringField('Agentes', validators=[DataRequired()])
    equipment_id = StringField('ID do Equipamento', validators=[Optional()])
    initial_km = IntegerField('KM Inicial', validators=[DataRequired()])
    final_km = IntegerField('KM Final', validators=[Optional()])
    toll = DecimalField('Pedágio', validators=[Optional()])
    
class ProviderForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    km_allowance = IntegerField('Franquia de KM', validators=[DataRequired()])
    hour_allowance = TimeField('Franquia de Hora', validators=[DataRequired()])
    activation_value = DecimalField('Valor do Acionamento', validators=[DataRequired()])
    km_excess_value = DecimalField('Valor KM Excedente', validators=[DataRequired()])
    excess_value = DecimalField('Valor Excedente', validators=[DataRequired()])
    
class ClientForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    km_allowance = IntegerField('Franquia de KM', validators=[DataRequired()])
    hour_allowance = TimeField('Franquia de Hora', validators=[DataRequired()])
    activation_value = DecimalField('Valor do Acionamento', validators=[DataRequired()])
    km_excess_value = DecimalField('Valor KM Excedente', validators=[DataRequired()])
    excess_value = DecimalField('Valor Excedente', validators=[DataRequired()])
    
class ActivationEditForm(ActivationForm):
    client = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    client_toll = DecimalField('Pedágio Cliente', validators=[DataRequired()])
    
class ProviderEditForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    km_allowance = IntegerField('Franquia de KM', validators=[DataRequired(), NumberRange(min=0)])
    hour_allowance = TimeField('Franquia de Hora', validators=[DataRequired()])  # Você pode querer usar um campo personalizado para a hora
    activation_value = DecimalField('Valor do Acionamento', validators=[DataRequired(), NumberRange(min=0)])
    km_excess_value = DecimalField('Valor KM Excedente', validators=[DataRequired(), NumberRange(min=0)])
    excess_value = DecimalField('Valor Excedente', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Atualizar')
    
class ClientEditForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    km_allowance = IntegerField('Franquia de KM', validators=[DataRequired(), NumberRange(min=0)])
    hour_allowance = TimeField('Franquia de Hora', validators=[DataRequired()])  # Você pode querer usar um campo personalizado para a hora
    activation_value = DecimalField('Valor do Acionamento', validators=[DataRequired(), NumberRange(min=0)])
    km_excess_value = DecimalField('Valor KM Excedente', validators=[DataRequired(), NumberRange(min=0)])
    excess_value = DecimalField('Valor Excedente', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Atualizar')