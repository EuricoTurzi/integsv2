# routes.py
import os, io, json
from flask import render_template, redirect, url_for, flash, send_file, request, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from flask_mail import Message
from app import app, mail
from forms import RegisterForm, LoginForm, ReportForm, ProfileForm, ChangePasswordForm, SalesRequestForm, EntranceForm
from models import db, User, Report, SalesRequest, Log, Notification, Entrance
from pdf_maintenance import generate_pdf
from pdf_expedition import generate_expedition_pdf
from pdf_sales import general_pdf
from pdf_entrance import generate_entrance_pdf
from datetime import datetime
from functools import wraps
import pandas as pd
from playsound import playsound

bcrypt = Bcrypt()

def create_notification(user, type, content):
    notification = Notification(user_id=user.id, type=type, content=content)
    db.session.add(notification)
    db.session.commit()
    user.unread_notifications += 1
    db.session.commit()

# Função para verificar as permissões do usuário
def check_permissions(access_level):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Verifica se o usuário está logado e se seu nível de acesso permite o acesso à rota
            if current_user.is_authenticated and current_user.access_level in access_level:
                return func(*args, **kwargs)
            else:
                # Caso o usuário não tenha permissão, redireciona para uma página de erro ou exibe uma mensagem adequada
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('index'))
        return wrapper
    return decorator

# def log_action(action):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             # Registra o log da ação    
#             timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

#             log_entry = {
#                 'action': action,
#                 'timestamp': timestamp,
#                 'user': current_user
#             }
#             db.session.add(Log(**log_entry))
#             db.session.commit()
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Verifica se o usuário existe no banco de dados
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)  # Autentica o usuário
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas. Por favor, tente novamente.', 'danger')

    return render_template('login.html', form=form)

# Rota de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Verifica se o nome de usuário já está em uso
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('O nome de usuário já está em uso. Por favor, escolha outro.', 'danger')
            return redirect(url_for('register'))

        # Cria um novo usuário
        new_user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        flash('Registrado com sucesso! Faça login para acessar sua conta.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/report', methods=['GET', 'POST'])
@login_required
@check_permissions(['Admin', 'Manutenção', 'Inteligência'])
def report():
    form = ReportForm()
    if form.validate_on_submit():
        # Obtenha os dados do formulário
        client_name = form.client_name.data
        reason = form.reason.data
        billing = form.billing.data
        model = form.model.data
        customization = form.customization.data
        equipment_number = form.equipment_number.data
        problem_type = form.problem_type.data
        photos = form.photos.data  # Lista de arquivos
        treatment = form.treatment.data

        # Salvar os arquivos no diretório de uploads e obter os caminhos dos arquivos
        image_paths = []
        for photo in photos:
            filename = secure_filename(photo.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(image_path)
            image_paths.append(image_path)

        # Serialize a lista de caminhos de imagem em uma string JSON
        image_paths_json = json.dumps(image_paths)

        # Crie um novo relatório no banco de dados com a lista serializada de caminhos de imagem
        new_report = Report(client_name=client_name, reason=reason, billing=billing, model=model,
                            customization=customization, equipment_number=equipment_number,
                            problem_type=problem_type, treatment=treatment, image_paths=image_paths_json)
        db.session.add(new_report)
        db.session.commit()

        # Criar a notificação
        inteligencia = User.query.filter_by(access_level='Inteligência').first()
        if inteligencia:
            create_notification(inteligencia, 'Uma manutenção foi realizada', 'Uma nova manutenção foi realizada.')
            playsound('static/img/alarme.mp3')

        # Registrar a ação no histórico
        action = f"Enviou um laudo de manutenção "
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()

        # Feedback para o usuário
        flash('Relatório enviado com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('report.html', form=form)

@app.route('/maintenances')
@check_permissions(['Admin', 'Inteligência', 'Manutenção'])
@login_required
def maintenances():
    page = request.args.get('page', 1, type=int)
    maintenances = Report.query.paginate(page=page, per_page=30)
    return render_template('maintenances.html', maintenances=maintenances)

def get_num_sales_requests():
    num_requests = SalesRequest.query.count()
    return num_requests

def get_num_maintenances():
    num_maintenances = Report.query.count()
    return num_maintenances

@app.route('/maintenances/direction')
@login_required
@check_permissions(['Admin','Diretoria','Inteligência'])
def direction_maintenance():
    page = request.args.get('page', 1, type=int)
    maintenances = Report.query.paginate(page=page, per_page=30)
    return render_template('direction_maintenance.html', maintenances=maintenances)

@app.route('/maintenances/update_direction/<int:maintenance_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'Manutenção','Inteligência'])
def update_direction(maintenance_id):
    maintenance = Report.query.get_or_404(maintenance_id)
    maintenance.status = 'Enviado à diretoria'
    db.session.commit()

    # Criar a notificação
    diretoria = User.query.filter_by(access_level='Diretoria').first()
    if diretoria:
        create_notification(diretoria, 'Uma manutenção foi enviada sem custo', 'Uma manutenção sem custo foi enviada para você.')
        playsound('static/img/alarme.mp3')

    flash('Status da entrada atualizado para "Manutenção realizada"!', 'info')
    return redirect(url_for('maintenances'))

@app.route('/approve-maintenance-direction/<int:maintenance_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'Inteligência'])
def approve_maintenance_direction(maintenance_id):
    maintenance = Report.query.get_or_404(maintenance_id)
    maintenance.status = 'Aprovado pela diretoria'
    db.session.commit()

    date_completed_datetime = datetime.strptime(maintenance.date_completed, '%d/%m/%Y %H:%M')

    # Gerar o PDF da manutenção
    pdf_data = generate_pdf({
        'id': maintenance.id,
        'client_name': maintenance.client_name,
        'reason': maintenance.reason,
        'billing': maintenance.billing,
        'model': maintenance.model,
        'customization': maintenance.customization,
        'equipment_number': maintenance.equipment_number,
        'problem_type': maintenance.problem_type,
        'photos': json.loads(maintenance.image_paths) if maintenance.image_paths else [],
        'treatment': maintenance.treatment,
        'status': maintenance.status,
        'date_completed': date_completed_datetime.strftime('%d/%m/%Y %H:%M'),
    }, app)

    # Nome do arquivo para o anexo de e-mail
    filename = f'Laudo de manutenção - {maintenance.client_name} - {maintenance_id}.pdf'

    # Registrar a ação no histórico
    action = f"Aprovou um laudo de manutenção - Sem Custo - ID: {maintenance_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()
    # Enviar e-mail com o PDF anexado
    send_email(subject=f'Laudo de Manutenção | {maintenance.client_name} - {maintenance_id}',
               recipients=['forex30592@losvtn.com'],
               text_body='text_place_holder',
               html_body=f'''
                <p>Prezados,</p></br>

                <p>É com satisfação que comunico a aprovação, pelo nosso CEO, da manutenção sem custos para o cliente <b>'{maintenance.client_name}'</b>, referente à manutenção <b>'{maintenance_id}'</b>. Esta decisão reafirma nosso compromisso com a excelência no serviço e a plena satisfação dos nossos clientes.</p></br>
                <p>Entendemos a importância da confiança que depositam em nossos serviços e, por isso, tomamos a iniciativa de realizar esta manutenção sem custos adicionais. Acreditamos que ações como esta fortalecem nossa parceria e reforçam o valor que atribuímos a cada cliente.</p></br>
                <p>Permaneço à disposição para quaisquer esclarecimentos adicionais que se façam necessários.</p></br>

                <p>Atenciosamente,</p></br>

                <p><b>Alison Gardão</b></p>
                <p>Diretor Operacional</p>
                <p><b>Grupo GoldenSat</b></p>
                ''',
               attachments=[(filename, 'application/pdf', pdf_data)])

    flash('Manutenção aprovada com sucesso! E-mail enviado.', 'success')
    return redirect(url_for('maintenances'))

@app.route('/admin/dashboard')
@login_required
@check_permissions(['Admin', 'Manutenção', 'Inteligência'])
def admin_dashboard():
    
    num_sales_requests = get_num_sales_requests()
    num_maintenances = get_num_maintenances()
    page = request.args.get('page', 1, type=int)
    # Obtém os registros de log de ações
    log_entries = Log.query.paginate(page=page, per_page=5)

    return render_template('admin_dashboard.html', num_sales_requests=num_sales_requests,
                           num_maintenances=num_maintenances, log_entries=log_entries)

@app.route('/admin/dashboard/export')
@login_required
@check_permissions(['Admin', 'Manutenção', 'Inteligência'])
def export_logs():
    logs = Log.query.all()
    data = [{"user_id": log.user_id, "action": log.action, "timestamp": log.timestamp} for log in logs]
    df = pd.DataFrame(data)
    df.to_excel('logs.xlsx', index=False)
    return send_file('logs.xlsx', as_attachment=True)

@app.route('/admin/dashboard/export_sales_requests')
@login_required
@check_permissions(['Admin', 'Manutenção', 'Inteligência'])
def export_sales_requests():
    sales_requests = SalesRequest.query.all()
    data = [{column.name: getattr(sr, column.name) for column in SalesRequest.__table__.columns} for sr in sales_requests]
    df = pd.DataFrame(data)
    df.to_excel('sales_requests.xlsx', index=False)
    return send_file('sales_requests.xlsx', as_attachment=True)

@app.route('/admin/dashboard/export_maintenances')
@login_required
@check_permissions(['Admin', 'Manutenção', 'Inteligência'])
def export_maintenances():
    reports = Report.query.all()
    data = [{column.name: getattr(report, column.name) for column in Report.__table__.columns} for report in reports]
    df = pd.DataFrame(data)
    df.to_excel('maintenances.xlsx', index=False)
    return send_file('maintenances.xlsx', as_attachment=True)

@app.route('/download-pdf/<int:maintenance_id>', methods=['POST'])
def download_maintenance_pdf(maintenance_id):
    # Recupere as informações da manutenção do banco de dados
    maintenance = Report.query.get_or_404(maintenance_id)

    # Converta a string de data para um objeto datetime
    date_completed_datetime = datetime.strptime(maintenance.date_completed, '%d/%m/%Y %H:%M')

    # Gere o PDF com base nas informações da manutenção
    pdf_data = generate_pdf({
        'id': maintenance.id,
        'client_name': maintenance.client_name,
        'reason': maintenance.reason,
        'billing': maintenance.billing,
        'model': maintenance.model,
        'customization': maintenance.customization,
        'equipment_number': maintenance.equipment_number,
        'problem_type': maintenance.problem_type,
        'photos': json.loads(maintenance.image_paths) if maintenance.image_paths else [],
        'treatment': maintenance.treatment,
        'status': maintenance.status,
        'date_completed': date_completed_datetime.strftime('%d/%m/%Y %H:%M'),
    }, app)

    # Nome do arquivo para o download
    filename = f'maintenance_report_{maintenance_id}.pdf'

    # Retorne o PDF como uma resposta para o cliente
    return send_file(
        io.BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@app.route('/edit-maintenance/<int:maintenance_id>', methods=['GET', 'POST'])
@check_permissions(['Admin', 'Manutenção', 'Inteligência'])
@login_required
def edit_maintenance(maintenance_id):
    # Recuperar a manutenção do banco de dados
    maintenance = Report.query.get_or_404(maintenance_id)
    
    # Verificar se o método HTTP é POST (ou seja, o formulário foi submetido)
    if request.method == 'POST':
        # Atualizar os campos da manutenção com base nos dados do formulário
        maintenance.client_name = request.form['client_name']
        maintenance.reason = request.form['reason']
        maintenance.billing = request.form['billing']
        maintenance.model = request.form['model']
        maintenance.customization = request.form['customization']
        maintenance.equipment_number = request.form['equipment_number']
        maintenance.problem_type = request.form['problem_type']
        maintenance.treatment = request.form['treatment']
        
        # Salvar as alterações no banco de dados
        db.session.commit()

        # Registrar a ação no histórico
        action = f"Editou um laudo de manutenção - ID: {maintenance_id}"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()
        
        # Redirecionar para a página de manutenções após a edição
        return redirect(url_for('rejected_maintenances'))
    
    # Renderizar o template de edição de manutenção
    return render_template('edit_maintenance.html', maintenance=maintenance)

@app.route('/edit-sales-request/<int:sales_request_id>', methods=['GET', 'POST'])
@check_permissions(['Admin', 'Inteligência'])
@login_required
def edit_sales_request(sales_request_id):
    # Recuperar a requisição do banco de dados
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    
    # Verificar se o método HTTP é POST (ou seja, o formulário foi submetido)
    if request.method == 'POST':
        # Atualizar os campos da requisição com base nos dados do formulário
        sales_request.cnpj = request.form['cnpj']
        sales_request.contract_start = request.form['contract_start']
        sales_request.vigency = request.form['vigency']
        sales_request.reason = request.form['reason']
        sales_request.client = request.form['client']
        sales_request.sales_rep = request.form['sales_rep']
        sales_request.contract_type = request.form['contract_type']
        sales_request.shipping = request.form['shipping']
        sales_request.address = request.form['address']
        sales_request.contact_person = request.form['contact_person']
        sales_request.email = request.form['email']
        sales_request.phone = request.form['phone']
        sales_request.quantity = request.form['quantity']
        sales_request.model = request.form['model']
        sales_request.customization = request.form['customization']
        sales_request.tp = request.form['tp']
        sales_request.charger = request.form['charger']
        sales_request.cable = request.form['cable']
        sales_request.invoice_type = request.form['invoice_type']
        sales_request.value = request.form['value']
        sales_request.total_value = request.form['total_value']
        sales_request.payment_method = request.form['payment_method']
        sales_request.observations = request.form['observations']
        
        # Salvar as alterações no banco de dados
        db.session.commit()

        # Registrar a ação no histórico
        action = f"Editou uma requisição - ID: {sales_request_id}"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()
        
        # Redirecionar para a página de requisições após a edição
        return redirect(url_for('all_sales_request'))
    
    # Renderizar o template de edição de manutenção
    return render_template('edit_sales_request.html', sales_request=sales_request)

@app.route('/delete-maintenance/<int:maintenance_id>', methods=['POST'])
@check_permissions(['Admin', 'Inteligência'])
@login_required
def delete_maintenance(maintenance_id):
    # Recuperar a manutenção do banco de dados
    maintenance = Report.query.get_or_404(maintenance_id)
    
    # Remover a manutenção do banco de dados
    db.session.delete(maintenance)
    db.session.commit()

    # Registrar a ação no histórico
    action = f"Apagou um laudo de manutenção - ID: {maintenance_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()
    
    # Redirecionar para a página de manutenções após a exclusão
    return redirect(url_for('maintenances'))

# Atualize a função profile() para incluir a rota de edição do perfil
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    num_sales_requests = get_num_sales_requests()
    num_maintenances = get_num_maintenances()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.profile_picture = form.profile_picture.data
        current_user.additional_info = form.additional_info.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.profile_picture.data = current_user.profile_picture
        form.additional_info.data = current_user.additional_info
    return render_template('profile.html', form=form, num_maintenances=num_maintenances, num_sales_requests=num_sales_requests)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.profile_picture = form.profile_picture.data
        current_user.additional_info = form.additional_info.data
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.profile_picture.data = current_user.profile_picture
        form.additional_info.data = current_user.additional_info
    return render_template('edit_profile.html', form=form)

@app.route('/profile/edit/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('profile'))
    return render_template('change_password.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout bem-sucedido!', 'success')
    return redirect(url_for('index'))

def send_email(subject, recipients, text_body, html_body, cc=None, attachments=None):
    msg = Message(subject, recipients=recipients, cc=cc)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    mail.send(msg)

@app.route('/approve-maintenance/<int:maintenance_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'Inteligência'])
def approve_maintenance(maintenance_id):
    maintenance = Report.query.get_or_404(maintenance_id)
    maintenance.status = 'Aprovado'
    db.session.commit()

    date_completed_datetime = datetime.strptime(maintenance.date_completed, '%d/%m/%Y %H:%M')

    # Gerar o PDF da manutenção
    pdf_data = generate_pdf({
        'id': maintenance.id,
        'client_name': maintenance.client_name,
        'reason': maintenance.reason,
        'billing': maintenance.billing,
        'model': maintenance.model,
        'customization': maintenance.customization,
        'equipment_number': maintenance.equipment_number,
        'problem_type': maintenance.problem_type,
        'photos': json.loads(maintenance.image_paths) if maintenance.image_paths else [],
        'treatment': maintenance.treatment,
        'status': maintenance.status,
        'date_completed': date_completed_datetime.strftime('%d/%m/%Y %H:%M'),
    }, app)

    # Nome do arquivo para o anexo de e-mail
    filename = f'Laudo de manutenção - {maintenance.client_name} - {maintenance_id}.pdf'

    # Registrar a ação no histórico
    action = f"Aprovou um laudo de manutenção - ID: {maintenance_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    client_name = maintenance.client_name[0] if isinstance(maintenance.client_name, list) else maintenance.client_name
    # Enviar e-mail com o PDF anexado
    send_email(subject=f'Laudo de Manutenção | {maintenance.client_name} - {maintenance_id}',
               recipients=['forex30592@losvtn.com'],
               text_body='text_place_holder',
               html_body=f'''
                <p>Prezados,</p>
                <p>Gostaria de informar que a manutenção <b>'{maintenance_id}'</b> do cliente <b>'{maintenance.client_name}'</b> referente ao equipamento foi concluída conforme agendado.</p>
                            
                <p>Anexei ao presente e-mail o protocolo de manutenção detalhando todas as atividades realizadas, as condições atuais do equipamento e quaisquer recomendações relevantes para garantir seu pleno 
                funcionamento.</p></br>
                            
                <p>Caso venham a surgir dúvidas, estou à disposição para esclarecê-las.</p></br>
                            
                <p>Atenciosamente,</p></br>
                            
                <p>Guilherme Amarante</p>
                <p>Laboratório Técnico</p>
                ''',
               attachments=[(filename, 'application/pdf', pdf_data)])

    flash('Manutenção aprovada com sucesso! E-mail enviado.', 'success')
    return redirect(url_for('maintenances'))

@app.route('/reject-maintenance/<int:maintenance_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'Inteligência'])
def reject_maintenance(maintenance_id):
    maintenance = Report.query.get_or_404(maintenance_id)
    maintenance.status = 'Rejeitado'
    db.session.commit()

    # Criar a notificação
    manutencao = User.query.filter_by(access_level='Manutenção').first()
    if manutencao:
        create_notification(manutencao, 'Uma manutenção foi rejeitada', 'Uma manutenção foi rejeitada, verifique os dados.')
        playsound('static/img/alarme.mp3')

    # Registrar a ação no histórico
    action = f"Rejeitou um laudo de manutenção - ID: {maintenance_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    flash('Manutenção rejeitada com sucesso!', 'success')
    return redirect(url_for('rejected_maintenances'))

@app.route('/maintenances/rejected')
@login_required
@check_permissions(['Admin', 'Manutenção','Inteligência'])
def rejected_maintenances():
    rejected_maintenances = Report.query.filter_by(status='Rejeitado').all()
    return render_template('rejected_maintenances.html', maintenances=rejected_maintenances)

@app.route('/send-maintenance/<int:maintenance_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'Manutenção','Inteligência'])
def send_maintenance(maintenance_id):
    maintenance = Report.query.get_or_404(maintenance_id)
    maintenance.status = "Editado"
    db.session.commit()

    # Criar a notificação
    inteligencia = User.query.filter_by(access_level='Inteligência').first()
    if inteligencia:
        create_notification(inteligencia, 'Uma manutenção foi editada', 'Uma manutenção foi editada.')
        playsound('static/img/alarme.mp3')

    # Registrar a ação no histórico
    action = f"Atualizou um laudo de manutenção para 'Editado' - ID: {maintenance_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    flash('Manutenção enviada para edição com sucesso!', 'success')
    return redirect(url_for('rejected_maintenances'))

@app.route('/sales_request', methods=['GET', 'POST'])
@login_required
@check_permissions(['Admin', 'Comercial','Inteligência'])
def sales_request():
    form = SalesRequestForm()
    if form.validate_on_submit():
        # Criar um novo objeto SalesRequest com os dados do formulário
        sales_request = SalesRequest(
            cnpj=form.cnpj.data,
            contract_start=form.contract_start.data,
            vigency=form.vigency.data,
            reason=form.reason.data,
            location = form.location.data,
            client=form.client.data,
            sales_rep=form.sales_rep.data,
            contract_type=form.contract_type.data,
            shipping=form.shipping.data,
            maintenance_number=form.maintenance_number.data,
            delivery_fee = form.delivery_fee.data,
            address=form.address.data,
            contact_person=form.contact_person.data,
            email=form.email.data,
            phone=form.phone.data,
            quantity=form.quantity.data,
            model=form.model.data,
            customization=form.customization.data,
            tp=form.tp.data,
            charger=form.charger.data,
            cable=form.cable.data,
            invoice_type=form.invoice_type.data,
            value=form.value.data,
            total_value=form.total_value.data,
            payment_method=form.payment_method.data,
            observations=form.observations.data,
            accept_terms=form.accept_terms.data,
        )
        
        db.session.add(sales_request)
        db.session.commit()

        # Criar a notificação
        ceo = User.query.filter_by(access_level='CEO').first()
        if ceo:
            create_notification(ceo, 'Nova Requisição de Venda', 'Uma nova requisição de venda foi criada.')
            playsound('static/img/alarme.mp3')

        # Registrar a ação no histórico
        action = f"Enviou uma requisição de venda"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()

        flash('Requisição de vendas enviada com sucesso!', 'success')
        return redirect(url_for('sales_request'))
    else:
          print(form.errors)
    return render_template('sales_request_form.html', form=form)

@app.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template('terms_and_conditions.html')

@app.route('/sales_request/ceo')
@login_required
@check_permissions(['Admin', 'CEO','Inteligência'])
def ceo_approval_requests():
    ceo_approval_requests = SalesRequest.query.all()
    return render_template('ceo_approval_requests.html', ceo_approval_requests=ceo_approval_requests)

@app.route('/approve_ceo_approval_request/<int:sales_request_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'CEO','Inteligência'])
def approve_ceo_approval_request(sales_request_id):
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    sales_request.status = 'Aprovado'
    db.session.commit()

    # Criar a notificação para todos os usuários com o nível de acesso 'Comercial'
    comerciais = User.query.filter_by(access_level='Comercial').all()
    for comercial in comerciais:
        create_notification(comercial, 'Uma requisição foi aprovada', 'Uma requisição foi aprovada pelo CEO.')
        playsound('static/img/alarme.mp3')

    # Criar a notificação para todos os usuários com o nível de acesso 'Configuração'
    configs = User.query.filter_by(access_level='Configuração').all()
    for config in configs:
        create_notification(config, 'Uma requisição foi aprovada', 'Uma requisição foi aprovada, realize a configuração.')
        playsound('static/img/alarme.mp3')

    # Registrar a ação no histórico
    action = f"Aprovou uma requisição de venda - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    flash('Requisição de venda aprovada pelo CEO com sucesso!', 'success')
    return redirect(url_for('ceo_approval_requests'))

@app.route('/reject_ceo_approval_request/<int:sales_request_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'CEO','Inteligência'])
def reject_ceo_approval_request(sales_request_id):
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    sales_request.status = 'Rejeitado'
    db.session.commit()

    # Criar a notificação para todos os usuários com o nível de acesso 'Comercial'
    comerciais = User.query.filter_by(access_level='Comercial').all()
    for comercial in comerciais:
        create_notification(comercial, 'Uma requisição foi rejeitada', 'Uma requisição foi rejeitada pelo CEO.')
        playsound('static/img/alarme.mp3')

    # Criar a notificação
    diretoria = User.query.filter_by(access_level='Diretoria').first()
    if diretoria:
        create_notification(diretoria, 'Uma requisição foi rejeitada', 'Uma requisição foi rejeitada pelo CEO.')
        playsound('static/img/alarme.mp3')

    # Registrar a ação no histórico
    action = f"Rejeitou uma requisição de venda - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    flash('Requisição de venda rejeitada pelo CEO!', 'danger')
    return redirect(url_for('ceo_approval_requests'))

@app.route('/sales_request/direction')
@login_required
@check_permissions(['Admin', 'Diretoria','Inteligência'])
def direction():
    direction = SalesRequest.query.all()
    return render_template('direction.html', direction=direction)

@app.route('/approve_direction/<int:sales_request_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'CEO','Inteligência'])
def approve_direction(sales_request_id):
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    sales_request.status = 'Aprovado pela diretoria'
    db.session.commit()

    # Criar a notificação para todos os usuários com o nível de acesso 'Comercial'
    comerciais = User.query.filter_by(access_level='Comercial').all()
    for comercial in comerciais:
        create_notification(comercial, 'Uma requisição foi aprovada', 'Uma requisição foi aprovada pela diretoria.')
        playsound('static/img/alarme.mp3')

    # Criar a notificação para todos os usuários com o nível de acesso 'Configuração'
    configs = User.query.filter_by(access_level='Configuração').all()
    for config in configs:
        create_notification(config, 'Uma requisição foi aprovada', 'Uma requisição foi aprovada, realize a configuração.')
        playsound('static/img/alarme.mp3')

    # Registrar a ação no histórico
    action = f"Aprovou uma requisição de venda - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    flash('Requisição de venda aprovada pela diretoria com sucesso!', 'success')
    return redirect(url_for('direction'))

@app.route('/reject_direction/<int:sales_request_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'CEO','Inteligência'])
def reject_direction(sales_request_id):
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    sales_request.status = 'Cancelado pela diretoria'
    db.session.commit()

    # Criar a notificação para todos os usuários com o nível de acesso 'Comercial'
    comerciais = User.query.filter_by(access_level='Comercial').all()
    for comercial in comerciais:
        create_notification(comercial, 'Uma requisição foi aprovada', 'Uma requisição foi rejeitada pela diretoria.')
        playsound('static/img/alarme.mp3')

    # Registrar a ação no histórico
    action = f"Cancelou uma requisição de venda - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    flash('Requisição de venda cancelada pela diretoria!', 'danger')
    return redirect(url_for('direction'))

@app.route('/sales_request/all')
@login_required
@check_permissions(['Admin', 'CEO','Comercial','Inteligência'])
def all_sales_requests():
    page = request.args.get('page', 1, type=int)
    all_requests = SalesRequest.query.paginate(page=page, per_page=30)
    return render_template('all_sales_requests.html', all_requests=all_requests)

@app.route('/sales_request/configuration')
@login_required
@check_permissions(['Admin', 'Configuração','Inteligência'])
def configuration():
    configuration_requests = SalesRequest.query.all()
    return render_template('configuration.html', configuration_requests=configuration_requests)

@app.route('/edit_equipment_numbers/<int:sales_request_id>', methods=['GET', 'POST'])
@login_required
@check_permissions(['Admin', 'Configuração','Inteligência'])
def edit_equipment_numbers(sales_request_id):
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    if request.method == 'POST':
        equipment_numbers = request.form.get('equipment_numbers')
        formatted_equipment_numbers = equipment_numbers.replace(" ", ";")
        sales_request.status = 'Pronto para o envio'
        sales_request.equipment_numbers = formatted_equipment_numbers
        db.session.commit()

        # Registrar a ação no histórico
        action = f"Inseriu os equipamentos ao laudo de requisição e atualizou para 'Pronto para o envio' - ID: {sales_request_id}"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()

        flash('Números dos equipamentos adicionados com sucesso! Status atualizado para "Pronto para o envio"!', 'success')
        return redirect(url_for('configuration'))
    return render_template('edit_equipment_numbers.html', sales_request=sales_request)

@app.route('/send_configuration_request/<int:sales_request_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'Configuração','Inteligência'])
def send_configuration_request(sales_request_id):
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    sales_request.status = 'Enviado para a expedição'
    db.session.commit()

    # Criar a notificação para todos os usuários com o nível de acesso 'Comercial'
    comerciais = User.query.filter_by(access_level='Comercial').all()
    for comercial in comerciais:
        create_notification(comercial, 'Uma requisição foi configurada', 'Uma requisição está pronta para a liberação')
        playsound('static/img/alarme.mp3')

    expedicaos = User.query.filter_by(access_level='Expedição').all()
    for expedicao in expedicaos:
        create_notification(expedicao, 'Uma requisição foi configurada', 'Uma requisição está pronta para a liberação')
        playsound('static/img/alarme.mp3')

    # Registrar a ação no histórico
    action = f"Liberou a requisição para a expedição - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    flash('Requisição enviada para a expedição!', 'info')
    return redirect(url_for('configuration'))

@app.route('/sales_request/expedition')
@login_required
@check_permissions(['Admin', 'Expedição','Inteligência'])
def expedition():
    expedition_requests = SalesRequest.query.all()
    return render_template('expedition.html', expedition_requests=expedition_requests)

@app.route('/mark_as_sent/<int:sales_request_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'Expedição','Inteligência'])
def mark_as_sent(sales_request_id):
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    sales_request.status = 'Pedido enviado ao cliente'

    # Atualize a data de envio ao cliente
    sales_request.date_sent_to_customer = datetime.now().strftime('%d/%m/%Y %H:%M')
    db.session.commit()

    # Criar a notificação para todos os usuários com o nível de acesso 'Comercial'
    comerciais = User.query.filter_by(access_level='Comercial').all()
    for comercial in comerciais:
        create_notification (comercial, 'Uma requisição foi enviada', 'Uma requisição foi enviada ao cliente.')
        playsound('static/img/alarme.mp3')

    date_completed_datetime = datetime.strptime(sales_request.date_completed, '%d/%m/%Y %H:%M')

    pdf_data = generate_expedition_pdf({
    'id': sales_request.id,
    'contract_type': sales_request.contract_type,
    'client': sales_request.client,
    'quantity': sales_request.quantity,
    'model': sales_request.model,
    'customization': sales_request.customization,
    'chargers': sales_request.charger,
    'cables': sales_request.cable,
    'address': sales_request.address,
    'ac': sales_request.contact_person,
    'equipment_numbers': sales_request.equipment_numbers,
    'date_completed': date_completed_datetime.strftime('%d/%m/%Y %H:%M'),
    }, app)

    # Nome do arquivo para o download
    filename = f'Protocolo de Saída - {sales_request.client} - {sales_request.id}.pdf'

    # Registrar a ação no histórico
    action = f"Enviou o pedido ao cliente - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    send_email(subject=f'Protocolo de Saída | {sales_request.client} - {sales_request_id}',
               recipients=['forex30592@losvtn.com'],
               cc=['forex30592@losvtn.com'],
               text_body='text_place_holder',
               html_body=f'''
                <p>Prezados(as)</p></br>

                <p>É com satisfação que informamos que os equipamentos referentes ao pedido <b>'{sales_request_id}'</b> do cliente <b>'{sales_request.client}'</b> foram liberados e já se encontram a caminho.</p>
                <p>Em anexo a este e-mail, você encontrará o protocolo de saída, que detalha todas as verificações realizadas, as condições de envio dos equipamentos </p><br>

                <p>Atenciosamente,</p><br>

                <p>Regina Gonçalves</p>
                <p>Expedição</p>
                <p>Grupo Golden Sat</p>
                ''',
               attachments=[(filename, 'application/pdf', pdf_data)])

    flash('Status da requisição atualizado para "Pedido enviado ao cliente"!', 'info')
    return redirect(url_for('expedition'))

@app.route('/download_pdf/<int:sales_request_id>')
@login_required
def download_pdf(sales_request_id):
    # Recupere as informações da requisição de expedição do banco de dados
    sales_request = SalesRequest.query.get_or_404(sales_request_id)

    date_completed_datetime = datetime.strptime(sales_request.date_completed, '%d/%m/%Y %H:%M')

    # Gere o PDF com base nas informações da requisição de expedição
    pdf_data = generate_expedition_pdf({
        'id': sales_request.id,
        'contract_type': sales_request.contract_type,
        'client': sales_request.client,
        'quantity': sales_request.quantity,
        'model': sales_request.model,
        'customization': sales_request.customization,
        'chargers': sales_request.charger,
        'cables': sales_request.cable,
        'address': sales_request.address,
        'ac': sales_request.contact_person,
        'equipment_numbers': sales_request.equipment_numbers,
        'date_completed': date_completed_datetime.strftime('%d/%m/%Y %H:%M'),
    }, app)

    # Nome do arquivo para o download
    filename = f'Protocolo de Saída - {sales_request.client} - {sales_request.id}.pdf'

    # Retorne o PDF como uma resposta para o cliente
    return send_file(
        io.BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@app.route('/download_sales_pdf/<int:sales_request_id>')
@login_required
def download_sales_pdf(sales_request_id):
    # Recupere as informações da requisição de expedição do banco de dados
    sales_request = SalesRequest.query.get_or_404(sales_request_id)

    date_completed_datetime = datetime.strptime(sales_request.date_completed, '%d/%m/%Y %H:%M')

    # Gere o PDF com base nas informações da requisição de expedição
    pdf_data = general_pdf({
        'id': sales_request.id,
        'cnpj': sales_request.cnpj,
        'contract_start': sales_request.contract_start,
        'vigency': sales_request.vigency,
        'reason': sales_request.reason,
        'location': sales_request.location if sales_request.shipping == 'Isca Fast' else None,
        'maintenance_number': sales_request.maintenance_number if sales_request.reason == 'Manutenção' else None,
        'client': sales_request.client,
        'sales_rep': sales_request.sales_rep,
        'contract_type': sales_request.contract_type,
        'shipping': sales_request.shipping,
        'delivery_fee': sales_request.delivery_fee if sales_request.shipping == 'Motoboy' else None,
        'address': sales_request.address,
        'contact_person': sales_request.contact_person,
        'email': sales_request.email,
        'phone': sales_request.phone,
        'quantity': sales_request.quantity,
        'model': sales_request.model,
        'customization': sales_request.customization,
        'tp': sales_request.tp,
        'charger': sales_request.charger,
        'cable': sales_request.cable,
        'invoice_type': sales_request.invoice_type,
        'value': sales_request.value,
        'total_value': sales_request.total_value,
        'payment_method': sales_request.payment_method,
        'observations': sales_request.observations,
        'date_completed': date_completed_datetime.strftime('%d/%m/%Y %H:%M'),
    }, app)

    # Nome do arquivo para o download
    filename = f'Protocolo de Requisição - {sales_request.client} - {sales_request.id}.pdf'

    # Retorne o PDF como uma resposta para o cliente
    return send_file(
        io.BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@app.route('/get_notifications')
@login_required
def get_notifications():
    notifications = [{
        'content': n.content,
        'timestamp': n.timestamp.strftime('%d/%m/%Y %H:%M'),
        'id': n.id  # Certifique-se de que o ID da notificação está sendo incluído
    } for n in current_user.notifications]
    return jsonify({
        'unread_notifications': current_user.unread_notifications,
        'notifications': notifications
    })

@app.route('/mark_as_read/<int:notification_id>')
@login_required
def mark_as_read(notification_id):
    notification = Notification.query.get(notification_id)
    if notification and notification.user_id == current_user.id:
        db.session.delete(notification)  # Excluir a notificação
        current_user.unread_notifications -= 1  # Atualizar o contador de notificações não lidas
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/admin/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@check_permissions(['Admin','Inteligência'])
def edit_user(id):
    user = User.query.get(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.profile_picture = request.form['profile_picture']
        user.additional_info = request.form['additional_info']
        user.access_level = request.form['access_level']
        db.session.commit()
        return redirect(url_for('users', id=user.id))
    return render_template('edit_user.html', user=user)

@app.route('/admin/users', methods=['GET'])
@login_required
@check_permissions(['Admin','Inteligência'])
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/sales_request/status')
@login_required
def sales_status():
    status_sales = SalesRequest.query.all()
    return render_template('sales_status.html', status_sales=status_sales)

@app.route('/entrance', methods=['GET', 'POST'])
@login_required
@check_permissions(['Admin', 'Expedição', 'Inteligência'])
def entrance():
    form = EntranceForm()
    if form.validate_on_submit():
        form.process_equipment_number()  # Processa os números dos equipamentos
        # Criar um novo objeto SalesRequest com os dados do formulário
        entrance = Entrance(
            client=form.client.data,
            entrance_type=form.entrance_type.data,
            model=form.model.data,
            customization=form.customization.data,
            type_of_receipt=form.type_of_receipt.data,
            recipients_name=form.recipients_name.data,
            withdrawn_by=form.withdrawn_by.data,
            equipment_numbers=form.equipment_number.data,  # Adiciona os números dos equipamentos
            accept_terms=form.accept_terms.data,
        )
        
        db.session.add(entrance)
        db.session.commit()

        # Gerar o PDF
        pdf_data = generate_entrance_pdf(entrance, app)

        # Criar a notificação
        manutencao = User.query.filter_by(access_level='Manutenção').first()
        if manutencao:
            create_notification(manutencao, 'Uma entrada de equipamento foi realizada', 'Uma entrada de equipamento foi realizada')
            playsound('static/img/alarme.mp3')

        # Registrar a ação no histórico
        action = f"Deu entrada em equipamentos"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()

        # Nome do arquivo para o download
        filename = f'Protocolo de Entrada - {entrance.client} - {entrance.id}.pdf'

        send_email(subject=f'Protocolo de Entrada | {entrance.client} - {entrance.id}',
                   recipients=['forex30592@losvtn.com'],
                   cc=['forex30592@losvtn.com'],
                   text_body='text_place_holder',
                   html_body=f'''
                    <p>Prezados(as)</p></br>

                    <p>É com satisfação que informamos que os equipamentos referentes ao pedido <b>'{entrance.id}'</b> do cliente <b>'{entrance.client}'</b> foram recebidos.</p>
                    <p>Em anexo a este e-mail, você encontrará o protocolo de entrada, que detalha todas as verificações realizadas, as condições de recebimento dos equipamentos </p><br>

                    <p>Atenciosamente,</p><br>

                    <p>Regina Gonçalves</p>
                    <p>Expedição</p>
                    <p>Grupo Golden Sat</p>
                    ''',
                   attachments=[(filename, 'application/pdf', pdf_data)])

        flash('Entrada de equipamentos realizada com sucesso!', 'success')
        return redirect(url_for('entrance'))
    else:
          print(form.errors)
    return render_template('entrance_form.html', form=form)

@app.route('/entrance/all')
@login_required
@check_permissions(['Admin', 'Manutenção','Expedição','Inteligência'])
def all_entrances():
    page = request.args.get('page', 1, type=int)
    all_entrances = Entrance.query.paginate(page=page, per_page=30)
    return render_template('entrances.html', all_entrances=all_entrances)

@app.route('/entrance/update_status/<int:entrance_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'Manutenção','Inteligência'])
def update_status(entrance_id):
    entrance = Entrance.query.get_or_404(entrance_id)
    entrance.status = 'Manutenção realizada'
    db.session.commit()

    flash('Status da entrada atualizado para "Manutenção realizada"!', 'info')
    return redirect(url_for('all_entrances'))

@app.route('/download_entrance_pdf/<int:entrance_id>', methods=['POST'])
def download_entrance_pdf(entrance_id):
    # Recupere as informações da manutenção do banco de dados
    entrance = Entrance.query.get_or_404(entrance_id)

    # Gere o PDF com base nas informações da manutenção
    pdf_data = generate_entrance_pdf(entrance, app)

    # Nome do arquivo para o download
    filename = f'Protocolo de Entrada - {entrance_id}.pdf'

    # Retorne o PDF como uma resposta para o cliente
    return send_file(
        io.BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )