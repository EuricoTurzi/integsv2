# routes.py
import os, io, json
from flask import render_template, redirect, url_for, flash, send_file, request, jsonify, make_response, Response
from flask_login import current_user, login_required, login_user, logout_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from flask_mail import Message
from app import app, mail
from forms import RegisterForm, LoginForm, ReportForm, ProfileForm, ChangePasswordForm, SalesRequestForm, EntranceForm, ReactivationForm, EquipmentStockForm, ActivationForm, ProviderForm, ClientForm, ActivationEditForm, ProviderEditForm, ClientEditForm
from models import db, User, Report, SalesRequest, Log, Entrance, Reactivation, Equipment, EquipmentStock, Activation, Provider, Client
from pdf_maintenance import generate_pdf
from pdf_expedition import generate_expedition_pdf
from pdf_sales import general_pdf
from pdf_entrance import generate_entrance_pdf
from datetime import datetime
from functools import wraps
import pandas as pd
from io import BytesIO
from openpyxl import Workbook

bcrypt = Bcrypt()

EQUIPMENT_VALUES ={
    'GS 410': 152.50,
    'GS 4410': 295.00,
    'GS 449': 310.75,   
    'GS 33': 150.00,
    'Localizador GS310': 163.20,
    'Imobilizador GS340': 279.30,
    'ESEYE': 13.05,
    '1NCE': 10.00,
}

# Função para verificar as permissões do usuário
def check_permissions(access_level):
    # Define um decorador para verificar as permissões do usuário
    def decorator(func):
        # Usa a função wraps para preservar a assinatura da função original
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Verifica se o usuário está autenticado e se seu nível de acesso está na lista de níveis de acesso permitidos
            if current_user.is_authenticated and current_user.access_level in access_level:
                # Se o usuário tiver permissão, executa a função original
                return func(*args, **kwargs)
            else:
                # Se o usuário não tiver permissão, exibe uma mensagem de erro e redireciona para a página inicial
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('index'))
        # Retorna a função wrapper que será usada quando a função original for chamada
        return wrapper
    # Retorna o decorador que será aplicado à função original
    return decorator

# Rota da página inicial
@app.route('/')
def index():
    # Renderiza o template 'index.html' quando a página inicial é acessada
    return render_template('index.html')

# Rota da página de login do usuário
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Cria uma instância do formulário de login
    form = LoginForm()
    
    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Obtém os dados de usuário e senha do formulário
        username = form.username.data
        password = form.password.data

        # Verifica se o usuário existe no banco de dados
        user = User.query.filter_by(username=username).first()
        
        # Se o usuário existir e a senha estiver correta, autentica o usuário
        if user and user.check_password(password):
            login_user(user)  # Autentica o usuário
            flash('Login bem-sucedido!', 'success')
            # Redireciona para a página inicial após o login bem-sucedido
            return redirect(url_for('index'))
        else:
            # Se as credenciais estiverem inválidas, exibe uma mensagem de erro
            flash('Credenciais inválidas. Por favor, tente novamente.', 'danger')

    # Renderiza a página de login com o formulário
    return render_template('login.html', form=form)

# Rota de registro do usuário
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Cria uma instância do formulário de registro
    form = RegisterForm()
    
    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Obtém os dados de usuário, email e senha do formulário
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Verifica se o nome de usuário já está em uso
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            # Se o nome de usuário já estiver em uso, exibe uma mensagem de erro e redireciona para a página de registro
            flash('O nome de usuário já está em uso. Por favor, escolha outro.', 'danger')
            return redirect(url_for('register'))

        # Cria um novo usuário com o nome de usuário, email e senha fornecidos
        new_user = User(username=username, email=email, password_hash=generate_password_hash(password))
        # Adiciona o novo usuário à sessão do banco de dados
        db.session.add(new_user)
        # Confirma as alterações na sessão do banco de dados, efetivamente salvando o novo usuário no banco de dados
        db.session.commit()

        # Exibe uma mensagem de sucesso e redireciona para a página de login
        flash('Registrado com sucesso! Faça login para acessar sua conta.', 'success')
        return redirect(url_for('login'))
    
    # Renderiza a página de registro com o formulário
    return render_template('register.html', form=form)

# Rota do formulário de manutenção
@app.route('/report', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Manutenção', 'Inteligência'])  # Verifica as permissões do usuário
def report():
    # Cria uma instância do formulário de manutenção
    form = ReportForm()
    
    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Obtém os dados do formulário
        client_name = form.client_name.data
        reason = form.reason.data
        billing = form.billing.data
        model = form.model.data
        customization = form.customization.data
        equipment_number = form.equipment_number.data
        problem_type = form.problem_type.data
        photos = form.photos.data  # Lista de arquivos
        treatment = form.treatment.data

        # Salva os arquivos no diretório de uploads e obtém os caminhos dos arquivos
        image_paths = []
        for photo in photos:
            filename = secure_filename(photo.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(image_path)
            image_paths.append(image_path)

        # Serializa a lista de caminhos de imagem em uma string JSON
        image_paths_json = json.dumps(image_paths)

        # Cria um novo relatório no banco de dados com a lista serializada de caminhos de imagem
        new_report = Report(client_name=client_name, reason=reason, billing=billing, model=model,
                            customization=customization, equipment_number=equipment_number,
                            problem_type=problem_type, treatment=treatment, image_paths=image_paths_json)
        db.session.add(new_report)
        db.session.commit()

        # Registra a ação no histórico
        action = f"Enviou um laudo de manutenção "
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()

        # Feedback para o usuário
        flash('Relatório enviado com sucesso!', 'success')
        return redirect(url_for('report'))  # Redireciona para a página de relatório

    # Renderiza a página de relatório com o formulário
    return render_template('report.html', form=form)

# Rota de visualização das manutenções
@app.route('/maintenances')
@check_permissions(['Admin', 'Inteligência', 'Comercial', 'Diretoria', 'CEO', 'Manutenção'])
@login_required
def maintenances():
    # Obtém o número da página a partir dos argumentos da requisição, padrão é 1
    page = request.args.get('page', 1, type=int)
    # Obtém os relatórios de manutenção da página atual, com 30 relatórios por página
    maintenances = Report.query.paginate(page=page, per_page=30)
    # Renderiza a página de manutenções com os relatórios de manutenção
    return render_template('maintenances.html', maintenances=maintenances)

# Função para obter o número de solicitações de vendas
def get_num_sales_requests():
    # Conta o número de solicitações de vendas no banco de dados
    num_requests = SalesRequest.query.count()
    return num_requests

# Função para obter o número de manutenções
def get_num_maintenances():
    # Conta o número de relatórios de manutenção no banco de dados
    num_maintenances = Report.query.count()
    return num_maintenances

# Rota de visualização das manutenções (diretoria)
@app.route('/maintenances/direction')
@login_required
@check_permissions(['Admin', 'Diretoria', 'CEO', 'Inteligência'])
def direction_maintenance():
    # Obtém o número da página a partir dos argumentos da requisição, padrão é 1
    page = request.args.get('page', 1, type=int)
    
    # Obtém os relatórios de manutenção com status 'Enviado à diretoria' da página atual, com 30 relatórios por página
    maintenances = Report.query.filter_by(status='Enviado à diretoria').paginate(page=page, per_page=30)
    
    # Renderiza a página de manutenções da diretoria com os relatórios de manutenção
    return render_template('direction_maintenance.html', maintenances=maintenances)

# Rota de atualização de status de manutenção
@app.route('/maintenances/update_direction/<int:maintenance_id>', methods=['POST'])
@login_required
@check_permissions(['Admin', 'Inteligência'])
def update_direction(maintenance_id):
    # Obtém o relatório de manutenção pelo ID, ou retorna um erro 404 se não for encontrado
    maintenance = Report.query.get_or_404(maintenance_id)
    
    # Atualiza o status do relatório de manutenção para 'Enviado à diretoria'
    maintenance.status = 'Enviado à diretoria'
    
    # Confirma as alterações na sessão do banco de dados, efetivamente atualizando o status do relatório de manutenção no banco de dados
    db.session.commit()

    # Exibe uma mensagem de informação para o usuário
    flash('Status da entrada atualizado para "Manutenção realizada"!', 'info')
    
    # Redireciona para a página de manutenções
    return redirect(url_for('maintenances'))

# Rota de aprovação de manutenção e envio de e-mail
@app.route('/approve-maintenance-direction/<int:maintenance_id>', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Inteligência', 'Diretoria'])  # Verifica as permissões do usuário
def approve_maintenance_direction(maintenance_id):
    # Obtém o relatório de manutenção pelo ID, ou retorna um erro 404 se não for encontrado
    maintenance = Report.query.get_or_404(maintenance_id)
    
    # Atualiza o status do relatório de manutenção para 'Aprovado pela diretoria'
    maintenance.status = 'Aprovado pela diretoria'
    
    # Confirma as alterações na sessão do banco de dados, efetivamente atualizando o status do relatório de manutenção no banco de dados
    db.session.commit()

    # Converte a data de conclusão do relatório de manutenção para um objeto datetime
    date_completed_datetime = datetime.strptime(maintenance.date_completed, '%d/%m/%Y %H:%M')

    # Gera o PDF do relatório de manutenção
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

    # Define o nome do arquivo para o anexo de e-mail
    filename = f'Laudo de manutenção - {maintenance.client_name} - {maintenance_id}.pdf'

    # Registra a ação no histórico
    action = f"Aprovou um laudo de manutenção - Sem Custo - ID: {maintenance_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()
    
    # Envia um e-mail com o PDF anexado
    send_email(subject=f'Laudo de Manutenção | {maintenance.client_name} - {maintenance_id}',
               recipients=['comercial@grupogoldensat.com.br'],
               cc=['inteligencia@grupogoldensat.com.br', 'comercial2@grupogoldensat.com.br', 'mayra.monteiro@grupogoldensat.com.br', 'aux_financeiro@grupogoldensat.com.br'],
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

    # Exibe uma mensagem de sucesso para o usuário
    flash('Manutenção aprovada com sucesso! E-mail enviado.', 'success')
    
    # Redireciona para a página de manutenções
    return redirect(url_for('maintenances'))

# Rota de visualização do Dashboard administrativo
@app.route('/admin/dashboard')
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'CEO', 'Inteligência'])  # Verifica as permissões do usuário
def admin_dashboard():

    # Função para obter o valor total das vendas
    def get_total_sales_values():
        # Calcula a soma dos valores totais de todas as solicitações de vendas
        total_value = db.session.query(db.func.sum(SalesRequest.total_value)).scalar()
        # Retorna o valor total se não for None, caso contrário retorna 0
        return total_value if total_value is not None else 0
    
    # Função para obter o número de equipamentos reativados
    def get_num_reactivated_equipments():
        # Conta o número de equipamentos que foram reativados
        return Equipment.query.filter(Equipment.reactivation_id.isnot(None)).count()
    
    # Função para obter o valor total do estoque
    def get_total_stock_value():
        # Obtém todos os equipamentos em estoque
        equipments = EquipmentStock.query.all()
        # Calcula o valor total do estoque multiplicando a quantidade em estoque de cada equipamento pelo seu valor
        total_value = sum(equipment.quantity_in_stock * EQUIPMENT_VALUES.get(equipment.model, 0) for equipment in equipments)
        # Retorna o valor total do estoque
        return total_value
    
    # Obtém o valor total das vendas
    total_sales_values = get_total_sales_values()
    # Obtém o valor total do estoque
    total_stock_value = get_total_stock_value()
    # Obtém o número de solicitações de vendas
    num_sales_requests = get_num_sales_requests()
    # Obtém o número de manutenções
    num_maintenances = get_num_maintenances()
    # Obtém o número de equipamentos reativados
    num_reactivated_equipments = get_num_reactivated_equipments()
    # Obtém o número da página a partir dos argumentos da requisição, padrão é 1
    page = request.args.get('page', 1, type=int)
    # Obtém as entradas de log da página atual, com 5 entradas por página
    log_entries = Log.query.paginate(page=page, per_page=5)

    # Renderiza o dashboard administrativo com os dados obtidos
    return render_template('admin_dashboard.html', num_sales_requests=num_sales_requests,
                           num_maintenances=num_maintenances, log_entries=log_entries,
                           total_sales_values=total_sales_values,  num_reactivated_equipments=num_reactivated_equipments,total_stock_value=total_stock_value)

# Rota para exportar o relatório de log
@app.route('/admin/dashboard/export')
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Inteligência', 'CEO'])  # Verifica as permissões do usuário
def export_logs():
    # Obtém todas as entradas de log
    logs = Log.query.all()
    
    # Cria uma lista de dicionários, onde cada dicionário contém os dados de uma entrada de log
    data = [{"user_id": log.user_id, "action": log.action, "timestamp": log.timestamp} for log in logs]
    
    # Cria um DataFrame do pandas com os dados das entradas de log
    df = pd.DataFrame(data)

    # Cria um objeto BytesIO para armazenar o arquivo Excel na memória
    output = BytesIO()
    
    # Cria um escritor Excel com o pandas e escreve o DataFrame para o arquivo Excel
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    # Retorna o ponteiro do objeto BytesIO para o início do arquivo
    output.seek(0)

    # Cria uma resposta com o arquivo Excel e configura o cabeçalho para forçar o download do arquivo
    response = Response(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = "attachment; filename=logs.xlsx"
    
    # Retorna a resposta
    return response

# Rota para exportar o relatório de vendas
@app.route('/admin/dashboard/export_sales_requests')
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Inteligência', 'CEO'])  # Verifica as permissões do usuário
def export_sales_requests():
    # Obtém todas as solicitações de vendas
    sales_requests = SalesRequest.query.all()
    
    # Cria uma lista de dicionários, onde cada dicionário contém os dados de uma solicitação de venda
    data = [{column.name: getattr(sr, column.name) for column in SalesRequest.__table__.columns} for sr in sales_requests]
    
    # Cria um DataFrame do pandas com os dados das solicitações de vendas
    df = pd.DataFrame(data)

    # Cria um objeto BytesIO para armazenar o arquivo Excel na memória
    output = BytesIO()
    
    # Cria um escritor Excel com o pandas e escreve o DataFrame para o arquivo Excel
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    # Retorna o ponteiro do objeto BytesIO para o início do arquivo
    output.seek(0)

    # Cria uma resposta com o arquivo Excel e configura o cabeçalho para forçar o download do arquivo
    response = Response(output.getvalue(), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = "attachment; filename=sales_requests.xlsx"
    
    # Retorna a resposta
    return response

# Rota para exportar o relatório de manutenções
@app.route('/admin/dashboard/export_maintenances')
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Inteligência', 'CEO'])  # Verifica as permissões do usuário
def export_maintenances():
    # Obtém todos os relatórios de manutenção
    reports = Report.query.all()
    
    # Cria uma lista de dicionários, onde cada dicionário contém os dados de um relatório de manutenção
    data = [{column.name: getattr(report, column.name) for column in Report.__table__.columns} for report in reports]
    
    # Cria um DataFrame do pandas com os dados dos relatórios de manutenção
    df = pd.DataFrame(data)

    # Cria um objeto BytesIO para armazenar o arquivo Excel na memória
    output = BytesIO()
    
    # Cria um escritor Excel com o pandas e escreve o DataFrame para o arquivo Excel
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    # Retorna o ponteiro do objeto BytesIO para o início do arquivo
    output.seek(0)

    # Cria uma resposta com o arquivo Excel e configura o cabeçalho para forçar o download do arquivo
    response = Response(output.getvalue(), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = "attachment; filename=maintenances.xlsx"
    
    # Retorna a resposta
    return response

# Rota para baixar o pdf de manutenção
@app.route('/download-pdf/<int:maintenance_id>', methods=['POST'])
def download_maintenance_pdf(maintenance_id):
    # Recupera as informações da manutenção do banco de dados
    maintenance = Report.query.get_or_404(maintenance_id)

    # Converte a string de data para um objeto datetime
    date_completed_datetime = datetime.strptime(maintenance.date_completed, '%d/%m/%Y %H:%M')

    # Gera o PDF com base nas informações da manutenção
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

    # Define o nome do arquivo para o download
    filename = f'maintenance_report_{maintenance_id}.pdf'

    # Retorna o PDF como uma resposta para o cliente
    return send_file(
        io.BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

# Rota para edição da manutenção
@app.route('/edit-maintenance/<int:maintenance_id>', methods=['GET', 'POST'])
@check_permissions(['Admin', 'Manutenção', 'Inteligência'])  # Verifica as permissões do usuário
@login_required  # Requer que o usuário esteja autenticado
def edit_maintenance(maintenance_id):
    # Recupera a manutenção do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    maintenance = Report.query.get_or_404(maintenance_id)
    
    # Verifica se o método HTTP é POST (ou seja, o formulário foi submetido)
    if request.method == 'POST':
        # Atualiza os campos da manutenção com base nos dados do formulário
        maintenance.client_name = request.form['client_name']
        maintenance.reason = request.form['reason']
        maintenance.billing = request.form['billing']
        maintenance.model = request.form['model']
        maintenance.customization = request.form['customization']
        maintenance.equipment_number = request.form['equipment_number']
        maintenance.problem_type = request.form['problem_type']
        maintenance.treatment = request.form['treatment']
        
        # Salva as alterações no banco de dados
        db.session.commit()

        # Registra a ação no histórico
        action = f"Editou um laudo de manutenção - ID: {maintenance_id}"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()
        
        # Redireciona para a página de manutenções após a edição
        return redirect(url_for('rejected_maintenances'))
    
    # Renderiza o template de edição de manutenção
    return render_template('edit_maintenance.html', maintenance=maintenance)

# Rota para editar a requisição de venda
@app.route('/edit-sales-request/<int:sales_request_id>', methods=['GET', 'POST'])
@check_permissions(['Admin', 'Inteligência'])  # Verifica as permissões do usuário
@login_required  # Requer que o usuário esteja autenticado
def edit_sales_request(sales_request_id):
    # Recupera a requisição de venda do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    
    # Verifica se o método HTTP é POST (ou seja, o formulário foi submetido)
    if request.method == 'POST':
        # Atualiza os campos da requisição de venda com base nos dados do formulário
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
        
        # Salva as alterações no banco de dados
        db.session.commit()

        # Registra a ação no histórico
        action = f"Editou uma requisição - ID: {sales_request_id}"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()
        
        # Redireciona para a página de requisições após a edição
        return redirect(url_for('all_sales_request'))
    
    # Renderiza o template de edição de requisição de venda
    return render_template('edit_sales_request.html', sales_request=sales_request)

# Rota para excluir uma manutenção
@app.route('/delete-maintenance/<int:maintenance_id>', methods=['POST'])
@check_permissions(['Admin', 'Inteligência'])  # Verifica as permissões do usuário
@login_required  # Requer que o usuário esteja autenticado
def delete_maintenance(maintenance_id):
    # Recupera a manutenção do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    maintenance = Report.query.get_or_404(maintenance_id)
    
    # Remove a manutenção do banco de dados
    db.session.delete(maintenance)
    
    # Salva as alterações no banco de dados
    db.session.commit()

    # Registra a ação no histórico
    action = f"Apagou um laudo de manutenção - ID: {maintenance_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()
    
    # Redireciona para a página de manutenções após a exclusão
    return redirect(url_for('maintenances'))

# Rota para exibir o perfil do usuário
@app.route('/profile', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
def profile():
    # Cria uma instância do formulário de perfil
    form = ProfileForm()
    
    # Obtém o número de solicitações de vendas e manutenções
    num_sales_requests = get_num_sales_requests()
    num_maintenances = get_num_maintenances()
    
    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Atualiza os campos do usuário com base nos dados do formulário
        current_user.email = form.email.data
        current_user.profile_picture = form.profile_picture.data
        current_user.additional_info = form.additional_info.data
        
        # Salva as alterações no banco de dados
        db.session.commit()
        
        # Exibe uma mensagem de sucesso para o usuário
        flash('Profile updated successfully!', 'success')
        
        # Redireciona para a página de perfil após a atualização
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        # Preenche os campos do formulário com os dados atuais do usuário
        form.email.data = current_user.email
        form.profile_picture.data = current_user.profile_picture
        form.additional_info.data = current_user.additional_info
    
    # Renderiza o template de perfil com o formulário e o número de solicitações de vendas e manutenções
    return render_template('profile.html', form=form, num_maintenances=num_maintenances, num_sales_requests=num_sales_requests)

# Rota de edição do perfil do usuário
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
def edit_profile():
    # Cria uma instância do formulário de perfil
    form = ProfileForm()
    
    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Atualiza os campos do usuário com base nos dados do formulário
        current_user.email = form.email.data
        current_user.profile_picture = form.profile_picture.data
        current_user.additional_info = form.additional_info.data
        
        # Salva as alterações no banco de dados
        db.session.commit()
        
        # Exibe uma mensagem de sucesso para o usuário
        flash('Perfil atualizado com sucesso!', 'success')
        
        # Redireciona para a página de perfil após a atualização
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        # Preenche os campos do formulário com os dados atuais do usuário
        form.email.data = current_user.email
        form.profile_picture.data = current_user.profile_picture
        form.additional_info.data = current_user.additional_info
    
    # Renderiza o template de edição de perfil com o formulário
    return render_template('edit_profile.html', form=form)

# Rota para alteração de senha do usuário
@app.route('/profile/edit/change-password', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
def change_password():
    # Cria uma instância do formulário de alteração de senha
    form = ChangePasswordForm()
    
    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Atualiza a senha do usuário com base nos dados do formulário
        current_user.set_password(form.new_password.data)
        
        # Salva as alterações no banco de dados
        db.session.commit()
        
        # Exibe uma mensagem de sucesso para o usuário
        flash('Senha alterada com sucesso!', 'success')
        
        # Redireciona para a página de perfil após a alteração da senha
        return redirect(url_for('profile'))
    
    # Renderiza o template de alteração de senha com o formulário
    return render_template('change_password.html', form=form)

# Rota para logout da plataforma
@app.route('/logout')
@login_required  # Requer que o usuário esteja autenticado
def logout():
    # Faz o logout do usuário
    logout_user()
    
    # Exibe uma mensagem de sucesso para o usuário
    flash('Logout bem-sucedido!', 'success')
    
    # Redireciona para a página inicial após o logout
    return redirect(url_for('index'))

def send_email(subject, recipients, text_body, html_body, cc=None, attachments=None):
    # Cria uma nova mensagem de e-mail com o assunto e os destinatários fornecidos
    msg = Message(subject, recipients=recipients, cc=cc)
    
    # Define o corpo do texto e o corpo HTML da mensagem
    msg.body = text_body
    msg.html = html_body
    
    # Se houver anexos, anexa-os à mensagem
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    
    # Envia a mensagem
    mail.send(msg)

# Rota de aprovação da manutenção
@app.route('/approve-maintenance/<int:maintenance_id>', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Inteligência'])  # Verifica as permissões do usuário
def approve_maintenance(maintenance_id):
    # Recupera a manutenção do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    maintenance = Report.query.get_or_404(maintenance_id)
    
    # Atualiza o status da manutenção para 'Aprovado'
    maintenance.status = 'Aprovado'
    
    # Salva as alterações no banco de dados
    db.session.commit()

    # Converte a string de data para um objeto datetime
    date_completed_datetime = datetime.strptime(maintenance.date_completed, '%d/%m/%Y %H:%M')

    # Gera o PDF da manutenção
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

    # Define o nome do arquivo para o anexo de e-mail
    filename = f'Laudo de manutenção - {maintenance.client_name} - {maintenance_id}.pdf'

    # Registra a ação no histórico
    action = f"Aprovou um laudo de manutenção - ID: {maintenance_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    # Verifica se o nome do cliente é uma lista e, se for, obtém o primeiro elemento
    client_name = maintenance.client_name[0] if isinstance(maintenance.client_name, list) else maintenance.client_name
    
    # Envia um e-mail com o PDF anexado
    send_email(subject=f'Laudo de Manutenção | {maintenance.client_name} - {maintenance_id}',
               recipients=['comercial@grupogoldensat.com.br'],
               cc=['inteligencia@grupogoldensat.com.br', 'comercial2@grupogoldensat.com.br', 'mayra.monteiro@grupogoldensat.com.br', 'aux_financeiro@grupogoldensat.com.br'],
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

    # Exibe uma mensagem de sucesso para o usuário
    flash('Manutenção aprovada com sucesso! E-mail enviado.', 'success')
    
    # Redireciona para a página de manutenções após a aprovação
    return redirect(url_for('maintenances'))

# Rota para rejeitar a manutenção
@app.route('/reject-maintenance/<int:maintenance_id>', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Inteligência'])  # Verifica as permissões do usuário
def reject_maintenance(maintenance_id):
    # Recupera a manutenção do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    maintenance = Report.query.get_or_404(maintenance_id)
    
    # Atualiza o status da manutenção para 'Rejeitado'
    maintenance.status = 'Rejeitado'
    
    # Salva as alterações no banco de dados
    db.session.commit()

    # Registra a ação no histórico
    action = f"Rejeitou um laudo de manutenção - ID: {maintenance_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    # Exibe uma mensagem de sucesso para o usuário
    flash('Manutenção rejeitada com sucesso!', 'success')
    
    # Redireciona para a página de manutenções rejeitadas após a rejeição
    return redirect(url_for('rejected_maintenances'))

# Rota para exibir as manutenções rejeitadas
@app.route('/maintenances/rejected')
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Manutenção', 'Inteligência', 'Diretoria', 'CEO'])  # Verifica as permissões do usuário
def rejected_maintenances():
    # Recupera todas as manutenções com status 'Rejeitado' do banco de dados
    rejected_maintenances = Report.query.filter_by(status='Rejeitado').all()
    
    # Renderiza o template de manutenções rejeitadas com as manutenções rejeitadas
    return render_template('rejected_maintenances.html', maintenances=rejected_maintenances)

# Rota para alterar o status da manutenção após editar
@app.route('/send-maintenance/<int:maintenance_id>', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Manutenção', 'Inteligência'])  # Verifica as permissões do usuário
def send_maintenance(maintenance_id):
    # Recupera a manutenção do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    maintenance = Report.query.get_or_404(maintenance_id)
    
    # Atualiza o status da manutenção para 'Editado'
    maintenance.status = "Editado"
    
    # Salva as alterações no banco de dados
    db.session.commit()

    # Registra a ação no histórico
    action = f"Atualizou um laudo de manutenção para 'Editado' - ID: {maintenance_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    # Exibe uma mensagem de sucesso para o usuário
    flash('Manutenção enviada para edição com sucesso!', 'success')
    
    # Redireciona para a página de manutenções rejeitadas após a edição
    return redirect(url_for('rejected_maintenances'))

# Rota do formulário de requisição de venda
@app.route('/sales_request', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Comercial', 'Inteligência'])  # Verifica as permissões do usuário
def sales_request():
    # Cria uma instância do formulário de requisição de venda
    form = SalesRequestForm()
    
    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Cria um novo objeto SalesRequest com os dados do formulário
        sales_request = SalesRequest(
            cnpj=form.cnpj.data,
            contract_start=form.contract_start.data,
            vigency=form.vigency.data,
            reason=form.reason.data,
            location=form.location.data,
            client=form.client.data,
            sales_rep=form.sales_rep.data,
            contract_type=form.contract_type.data,
            shipping=form.shipping.data,
            maintenance_number=form.maintenance_number.data,
            delivery_fee=form.delivery_fee.data,
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
        
        # Verifica se há estoque suficiente antes de confirmar a venda
        equipment_stock = EquipmentStock.query.filter_by(model=form.model.data).first()
        if equipment_stock and equipment_stock.quantity_in_stock >= form.quantity.data:
            # Atualiza o estoque
            equipment_stock.quantity_in_stock -= form.quantity.data
            
            # Adiciona a requisição de venda à sessão do banco de dados
            db.session.add(sales_request)
            
            # Salva as alterações no banco de dados
            db.session.commit()

            # Registra a ação no histórico
            action = f"Enviou uma requisição de venda"
            log = Log(user_id=current_user.username, action=action)
            db.session.add(log)
            db.session.commit()

            # Exibe uma mensagem de sucesso para o usuário
            flash('Requisição de vendas enviada com sucesso e estoque atualizado!', 'success')
            
            # Redireciona para a página de requisição de venda após a submissão
            return redirect(url_for('sales_request'))
        else:
            # Se não houver estoque suficiente, exibe uma mensagem de erro para o usuário
            flash('Quantidade insuficiente no estoque para o modelo solicitado.', 'danger')

    # Renderiza o template do formulário de requisição de venda com o formulário
    return render_template('sales_request_form.html', form=form)

# Rota para exibir os termos e condições
@app.route('/terms_and_conditions')
def terms_and_conditions():
    # Renderiza o template 'terms_and_conditions.html'
    return render_template('terms_and_conditions.html')

# Rota para exibir as vendas ao CEO
@app.route('/sales_request/ceo')
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'CEO', 'Inteligência', 'Diretoria'])  # Verifica as permissões do usuário
def ceo_approval_requests():
    # Recupera todas as requisições de venda do banco de dados
    ceo_approval_requests = SalesRequest.query.all()
    
    # Renderiza o template 'ceo_approval_requests.html' com as requisições de venda
    return render_template('ceo_approval_requests.html', ceo_approval_requests=ceo_approval_requests)

# Rota para aprovar uma venda
@app.route('/approve_ceo_approval_request/<int:sales_request_id>', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'CEO', 'Inteligência', 'Diretoria'])  # Verifica as permissões do usuário
def approve_ceo_approval_request(sales_request_id):
    # Recupera a requisição de venda do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    
    # Atualiza o status da requisição de venda para 'Aprovado'
    sales_request.status = 'Aprovado'
    
    # Salva as alterações no banco de dados
    db.session.commit()

    # Registra a ação no histórico
    action = f"Aprovou uma requisição de venda - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    # Exibe uma mensagem de sucesso para o usuário
    flash('Requisição de venda aprovada pelo CEO com sucesso!', 'success')
    
    # Redireciona para a página de requisições de venda aprovadas pelo CEO após a aprovação
    return redirect(url_for('ceo_approval_requests'))

# Rota para rejeitar a venda
@app.route('/reject_ceo_approval_request/<int:sales_request_id>', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'CEO', 'Inteligência', 'Diretoria'])  # Verifica as permissões do usuário
def reject_ceo_approval_request(sales_request_id):
    # Recupera a requisição de venda do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    
    # Atualiza o status da requisição de venda para 'Rejeitado'
    sales_request.status = 'Rejeitado'
    
    # Salva as alterações no banco de dados
    db.session.commit()

    # Registra a ação no histórico
    action = f"Rejeitou uma requisição de venda - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    # Exibe uma mensagem de erro para o usuário
    flash('Requisição de venda rejeitada pelo CEO!', 'danger')
    
    # Redireciona para a página de requisições de venda aprovadas pelo CEO após a rejeição
    return redirect(url_for('ceo_approval_requests'))

# Rota para exibir as vendas para a diretoria
@app.route('/sales_request/direction')
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Diretoria', 'CEO', 'Inteligência'])  # Verifica as permissões do usuário
def direction():
    # Recupera todas as requisições de venda do banco de dados
    direction = SalesRequest.query.all()
    
    # Renderiza o template 'direction.html' com as requisições de venda
    return render_template('direction.html', direction=direction)

# Rota para aprovar a venda que foi rejeitada anteriormente
@app.route('/approve_direction/<int:sales_request_id>', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Diretoria', 'Inteligência', 'CEO'])  # Verifica as permissões do usuário
def approve_direction(sales_request_id):
    # Recupera a requisição de venda do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    
    # Atualiza o status da requisição de venda para 'Aprovado pela diretoria'
    sales_request.status = 'Aprovado pela diretoria'
    
    # Salva as alterações no banco de dados
    db.session.commit()

    # Registra a ação no histórico
    action = f"Aprovou uma requisição de venda - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    # Exibe uma mensagem de sucesso para o usuário
    flash('Requisição de venda aprovada pela diretoria com sucesso!', 'success')
    
    # Redireciona para a página de requisições de venda aprovadas pela diretoria após a aprovação
    return redirect(url_for('direction'))

# Rota para cancelar a venda
@app.route('/reject_direction/<int:sales_request_id>', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Diretoria', 'Inteligência', 'CEO'])  # Verifica as permissões do usuário
def reject_direction(sales_request_id):
    # Recupera a requisição de venda do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    
    # Atualiza o status da requisição de venda para 'Cancelado pela diretoria'
    sales_request.status = 'Cancelado pela diretoria'
    
    # Salva as alterações no banco de dados
    db.session.commit()

    # Registra a ação no histórico
    action = f"Cancelou uma requisição de venda - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    # Exibe uma mensagem de erro para o usuário
    flash('Requisição de venda cancelada pela diretoria!', 'danger')
    
    # Redireciona para a página de requisições de venda aprovadas pela diretoria após o cancelamento
    return redirect(url_for('direction'))

# Rota para exibir todas as vendas
@app.route('/sales_request/all')
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'CEO', 'Comercial', 'Diretoria', 'Inteligência'])  # Verifica as permissões do usuário
def all_sales_requests():
    # Obtém o número da página a partir dos argumentos da requisição, padrão é 1
    page = request.args.get('page', 1, type=int)
    
    # Obtém todas as requisições de venda da página atual, com 30 requisições por página
    all_requests = SalesRequest.query.paginate(page=page, per_page=30)
    
    # Renderiza o template 'all_sales_requests.html' com todas as requisições de venda
    return render_template('all_sales_requests.html', all_requests=all_requests)

# Rota para exibir as vendas para o setor de configuração
@app.route('/sales_request/configuration')
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Configuração', 'Inteligência'])  # Verifica as permissões do usuário
def configuration():
    # Obtém todas as requisições de venda do banco de dados
    configuration_requests = SalesRequest.query.all()
    
    # Renderiza o template 'configuration.html' com as requisições de venda
    return render_template('configuration.html', configuration_requests=configuration_requests)

# Rota para configurar os números de equipamentos da venda
@app.route('/edit_equipment_numbers/<int:sales_request_id>', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Configuração', 'Inteligência'])  # Verifica as permissões do usuário
def edit_equipment_numbers(sales_request_id):
    # Recupera a requisição de venda do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    
    # Verifica se o método HTTP é POST (ou seja, o formulário foi submetido)
    if request.method == 'POST':
        # Obtém os números dos equipamentos do formulário
        equipment_numbers = request.form.get('equipment_numbers')
        
        # Formata os números dos equipamentos substituindo espaços por ponto e vírgula
        formatted_equipment_numbers = equipment_numbers.replace(" ", ";")
        
        # Atualiza o status da requisição de venda para 'Pronto para o envio'
        sales_request.status = 'Pronto para o envio'
        
        # Atualiza os números dos equipamentos da requisição de venda
        sales_request.equipment_numbers = formatted_equipment_numbers
        
        # Salva as alterações no banco de dados
        db.session.commit()

        # Registra a ação no histórico
        action = f"Inseriu os equipamentos ao laudo de requisição e atualizou para 'Pronto para o envio' - ID: {sales_request_id}"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()

        # Exibe uma mensagem de sucesso para o usuário
        flash('Números dos equipamentos adicionados com sucesso! Status atualizado para "Pronto para o envio"!', 'success')
        
        # Redireciona para a página de configuração após a submissão
        return redirect(url_for('configuration'))
    
    # Renderiza o template de edição dos números dos equipamentos com a requisição de venda
    return render_template('edit_equipment_numbers.html', sales_request=sales_request)

# Rota para encaminhar a venda para a expedição
@app.route('/send_configuration_request/<int:sales_request_id>', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Configuração', 'Inteligência'])  # Verifica as permissões do usuário
def send_configuration_request(sales_request_id):
    # Recupera a requisição de venda do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    
    # Atualiza o status da requisição de venda para 'Enviado para a expedição'
    sales_request.status = 'Enviado para a expedição'
    
    # Salva as alterações no banco de dados
    db.session.commit()

    # Registra a ação no histórico
    action = f"Liberou a requisição para a expedição - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    # Exibe uma mensagem de informação para o usuário
    flash('Requisição enviada para a expedição!', 'info')
    
    # Redireciona para a página de configuração após o envio
    return redirect(url_for('configuration'))

# Rota para exibir as vendas para a expedição
@app.route('/sales_request/expedition')
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Expedição', 'CEO', 'Inteligência', 'Diretoria'])  # Verifica as permissões do usuário
def expedition():
    # Recupera todas as requisições de venda do banco de dados
    expedition_requests = SalesRequest.query.all()
    
    # Renderiza o template 'expedition.html' com as requisições de venda
    return render_template('expedition.html', expedition_requests=expedition_requests)

# Rota para enviar o e-mail e alterar o status da venda 
@app.route('/mark_as_sent/<int:sales_request_id>', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Expedição', 'Inteligência'])  # Verifica as permissões do usuário
def mark_as_sent(sales_request_id):
    # Recupera a requisição de venda do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    sales_request = SalesRequest.query.get_or_404(sales_request_id)
    
    # Atualiza o status da requisição de venda para 'Pedido enviado ao cliente'
    sales_request.status = 'Pedido enviado ao cliente'

    # Atualiza a data de envio ao cliente
    sales_request.date_sent_to_customer = datetime.now().strftime('%d/%m/%Y %H:%M')
    db.session.commit()

    # Converte a string de data para um objeto datetime
    date_completed_datetime = datetime.strptime(sales_request.date_completed, '%d/%m/%Y %H:%M')

    # Gera o PDF da requisição de venda
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

    # Define o nome do arquivo para o download
    filename = f'Protocolo de Saída - {sales_request.client} - {sales_request.id}.pdf'

    # Registra a ação no histórico
    action = f"Enviou o pedido ao cliente - ID: {sales_request_id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()

    # Envia um e-mail com o PDF anexado
    send_email(subject=f'Protocolo de Saída | {sales_request.client} - {sales_request_id}',
               recipients=['comercial@grupogoldensat.com.br'],
               cc=['inteligencia@grupogoldensat.com.br', 'atendimento@grupogoldensat.com.br', 'diretoria@grupogoldensat.com.br', 'superintendente@grupogoldensat.com.br', 'diretor.operacional@grupogoldensat.com.br', 'comercial2@grupogoldensat.com.br'],
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

    # Exibe uma mensagem de informação para o usuário
    flash('Status da requisição atualizado para "Pedido enviado ao cliente"!', 'info')
    
    # Redireciona para a página de expedição após o envio
    return redirect(url_for('expedition'))

# Rota para baixar o pdf de saida de venda
@app.route('/download_pdf/<int:sales_request_id>')
@login_required  # Requer que o usuário esteja autenticado
def download_pdf(sales_request_id):
    # Recupera a requisição de venda do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    sales_request = SalesRequest.query.get_or_404(sales_request_id)

    # Converte a string de data para um objeto datetime
    date_completed_datetime = datetime.strptime(sales_request.date_completed, '%d/%m/%Y %H:%M')

    # Gera o PDF com base nas informações da requisição de venda
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

    # Define o nome do arquivo para o download
    filename = f'Protocolo de Saída - {sales_request.client} - {sales_request.id}.pdf'

    # Retorna o PDF como uma resposta para o cliente
    return send_file(
        io.BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

# Rota para baixar o pdf de venda
@app.route('/download_sales_pdf/<int:sales_request_id>')
@login_required  # Requer que o usuário esteja autenticado
def download_sales_pdf(sales_request_id):
    # Recupera a requisição de venda do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    sales_request = SalesRequest.query.get_or_404(sales_request_id)

    # Converte a string de data para um objeto datetime
    date_completed_datetime = datetime.strptime(sales_request.date_completed, '%d/%m/%Y %H:%M')

    # Gera o PDF com base nas informações da requisição de venda
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

    # Define o nome do arquivo para o download
    filename = f'Protocolo de Requisição - {sales_request.client} - {sales_request.id}.pdf'

    # Retorna o PDF como uma resposta para o cliente
    return send_file(
        io.BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

# Rota para edição de usuários, nível administrativo
@app.route('/admin/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Inteligência'])  # Verifica as permissões do usuário
def edit_user(id):
    # Recupera o usuário do banco de dados pelo ID
    user = User.query.get(id)
    
    # Verifica se o método HTTP é POST (ou seja, o formulário foi submetido)
    if request.method == 'POST':
        # Atualiza os campos do usuário com base nos dados do formulário
        user.username = request.form['username']
        user.email = request.form['email']
        user.profile_picture = request.form['profile_picture']
        user.additional_info = request.form['additional_info']
        user.access_level = request.form['access_level']
        
        # Salva as alterações no banco de dados
        db.session.commit()
        
        # Redireciona para a página de usuários após a edição
        return redirect(url_for('users', id=user.id))
    
    # Renderiza o template de edição de usuário com o usuário
    return render_template('edit_user.html', user=user)

# Rota para exibição dos usuários, nível administrativo
@app.route('/admin/users', methods=['GET'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Inteligência'])  # Verifica as permissões do usuário
def users():
    # Recupera todos os usuários do banco de dados
    users = User.query.all()
    
    # Renderiza o template 'users.html' com os usuários
    return render_template('users.html', users=users)

# Rota para exibição das vendas, filtrado para os usuários base
@app.route('/sales_request/status')
@login_required  # Requer que o usuário esteja autenticado
def sales_status():
    # Recupera todas as requisições de venda do banco de dados
    status_sales = SalesRequest.query.all()
    
    # Renderiza o template 'sales_status.html' com as requisições de venda
    return render_template('sales_status.html', status_sales=status_sales)

# Rota para o formulário de entrada de equipamentos e envio de e-mail
@app.route('/entrance', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Expedição', 'Inteligência'])  # Verifica as permissões do usuário
def entrance():
    # Cria uma instância do formulário de entrada
    form = EntranceForm()
    
    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        form.process_equipment_number()  # Processa os números dos equipamentos
        
        # Cria um novo objeto Entrance com os dados do formulário
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
        
        # Adiciona a entrada à sessão do banco de dados
        db.session.add(entrance)
        
        # Salva as alterações no banco de dados
        db.session.commit()

        # Gera o PDF da entrada
        pdf_data = generate_entrance_pdf(entrance, app)

        # Registra a ação no histórico
        action = f"Deu entrada em equipamentos"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()

        # Define o nome do arquivo para o download
        filename = f'Protocolo de Entrada - {entrance.client} - {entrance.id}.pdf'

        # Envia um e-mail com o PDF anexado
        send_email(subject=f'Protocolo de Entrada | {entrance.client} - {entrance.id}',
                   recipients=['labtecnico@grupogoldensat.com.br'],
                   cc=['diretoria@grupogoldensat.com.br', 'superintendente@grupogoldensat.com.br', 'thiago@grupogoldensat.com.br', 'diretor.operacional@grupogoldensat.com.br', 'quality@grupogoldensat.com.br', 'aux_financeiro@grupogoldensat.com.br', 'fabio.pegoraro@grupogoldensat.com.br', 'inteligencia@grupogoldensat.com.br', 'comercial@grupogoldensat.com.br', 'config@grupogoldensat.com.br', 'mayra.monteiro@grupogoldensat.com.br', 'comercial2@grupogoldensat.com.br', 'atendimento@grupogoldensat.com'],
                   text_body='text_place_holder',
                   html_body=f'''
                    <p>Prezados(as)</p></br>

                    <p>É com satisfação que informamos que os equipamentos referentes ao pedido <b>'{entrance.id}'</b> do cliente <b>'{entrance.client}'</b> foram recebidos.</p>
                    <p>Em anexo a este e-mail, você encontrará o protocolo de entrada, que detalha todas as verificações realizadas, as condições de recebimento dos equipamentos </p>

                    <p>Atenciosamente,</p><br>

                    <p>Regina Gonçalves</p>
                    <p>Expedição</p>
                    <p>Grupo Golden Sat</p>
                    ''',
                   attachments=[(filename, 'application/pdf', pdf_data)])

        # Exibe uma mensagem de sucesso para o usuário
        flash('Entrada de equipamentos realizada com sucesso!', 'success')
        
        # Redireciona para a página de entrada após a submissão
        return redirect(url_for('entrance'))
    else:
        print(form.errors)  # Imprime os erros do formulário no console
    
    # Renderiza o template do formulário de entrada com o formulário
    return render_template('entrance_form.html', form=form)

# Rota para a exibição de todas as entradas de equipamentos
@app.route('/entrance/all')
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Manutenção', 'Expedição', 'CEO', 'Inteligência', 'Diretoria'])  # Verifica as permissões do usuário
def all_entrances():
    # Obtém o número da página a partir dos argumentos da requisição, padrão é 1
    page = request.args.get('page', 1, type=int)
    
    # Obtém todas as entradas da página atual, com 30 entradas por página
    all_entrances = Entrance.query.paginate(page=page, per_page=30)
    
    # Renderiza o template 'entrances.html' com todas as entradas
    return render_template('entrances.html', all_entrances=all_entrances)

# Rota para alteração do status da entrada
@app.route('/entrance/update_status/<int:entrance_id>', methods=['POST'])
@check_permissions(['Admin', 'Manutenção', 'Inteligência'])  # Verifica as permissões do usuário
def update_entrance_status(entrance_id):
    # Recupera a entrada do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    entrance = Entrance.query.get_or_404(entrance_id)
    
    # Atualiza o status da manutenção para 'Manutenção realizada'
    entrance.maintenance_status = 'Manutenção realizada'
    
    # Atualiza os números dos equipamentos retornados com base nos dados do formulário
    entrance.returned_equipment_numbers = request.form.get('equipment_returned')  # Corrigir o nome do campo
    
    # Salva as alterações no banco de dados
    db.session.commit()

    # Exibe uma mensagem de informação para o usuário
    flash('Status da entrada atualizado para "Manutenção realizada"!', 'info')
    
    # Redireciona para a página de todas as entradas após a atualização do status
    return redirect(url_for('all_entrances'))

# Rota para baixar o pdf do protocolo de entrada
@app.route('/download_entrance_pdf/<int:entrance_id>', methods=['POST'])
def download_entrance_pdf(entrance_id):
    # Recupera a entrada do banco de dados pelo ID, ou retorna um erro 404 se não for encontrada
    entrance = Entrance.query.get_or_404(entrance_id)

    # Gera o PDF da entrada
    pdf_data = generate_entrance_pdf(entrance, app)

    # Define o nome do arquivo para o download
    filename = f'Protocolo de Entrada - {entrance_id}.pdf'

    # Retorna o PDF como uma resposta para o cliente
    return send_file(
        io.BytesIO(pdf_data),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

# Rota para o formulário de reativação
@app.route('/reactivation/form', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Comercial', 'Inteligência'])  # Verifica as permissões do usuário
def reactivation_form():
    # Cria uma instância do formulário de reativação
    form = ReactivationForm()
    
    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Cria um novo objeto Reactivation com os dados do formulário
        reactivation = Reactivation(
            client=form.client.data,
            reactivation_reason=form.reactivation_reason.data,
            request_channel=form.request_channel.data,
            value=form.value.data,
            total_value=form.total_value.data,
            observation=form.observation.data
        )
        
        # Adiciona a reativação à sessão do banco de dados
        db.session.add(reactivation)
        
        # Salva as alterações no banco de dados
        db.session.flush()

        # Processa cada par de ID e CCID
        for i in range(18):  # Assumindo que você tem no máximo 18 equipamentos
            equipment_id = request.form.get(f'equipments-{i}-equipment_id', None)
            equipment_ccid = request.form.get(f'equipments-{i}-equipment_ccid', None)
            if equipment_id and equipment_ccid:
                # Cria um novo objeto Equipment com os dados do formulário
                equipment = Equipment(
                    reactivation_id=reactivation.id,
                    equipment_id=equipment_id,
                    equipment_ccid=equipment_ccid
                )
                
                # Adiciona o equipamento à sessão do banco de dados
                db.session.add(equipment)

        # Salva as alterações no banco de dados
        db.session.commit()

        # Exibe uma mensagem de sucesso para o usuário
        flash('Reativação cadastrada com sucesso!', 'success')
        
        # Redireciona para o formulário de reativação após a submissão
        return redirect(url_for('reactivation_form'))

    # Renderiza o template do formulário de reativação com o formulário
    return render_template('reactivation_form.html', form=form)

# Rota para a exibição de todas as reativações
@app.route('/reactivation/all', methods=['GET'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Comercial', 'CEO', 'Inteligência', 'Diretoria'])  # Verifica as permissões do usuário
def reactivations():
    # Recupera todas as reativações do banco de dados
    reactivations = Reactivation.query.all()
    
    # Renderiza o template 'reactivations.html' com as reativações
    return render_template('reactivations.html', reactivations=reactivations)

# Rota para a exibição do estoque
@app.route('/stock', methods=['GET'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Inteligência', 'CEO'])  # Verifica as permissões do usuário
def view_stock():
    # Cria uma instância do formulário de entrada de estoque
    form_entry = EquipmentStockForm(prefix="entry")
    
    # Cria uma instância do formulário de retirada de estoque
    form_withdrawal = EquipmentStockForm(prefix="withdrawal")
    
    # Recupera todo o estoque de equipamentos do banco de dados
    equipment_stock = EquipmentStock.query.all()
    
    # Renderiza o template 'stock_management.html' com os formulários e o estoque de equipamentos
    return render_template('stock_management.html', 
                           form_entry=form_entry, 
                           form_withdrawal=form_withdrawal, 
                           equipment_stock=equipment_stock)

# Rota para adicionar os itens no estoque
@app.route('/stock/add', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Inteligência'])  # Verifica as permissões do usuário
def add_to_stock():
    # Recupera o modelo do equipamento e a quantidade do formulário
    model = request.form.get('entry-model')
    quantity_str = request.form.get('entry-quantity_in_stock')
    
    # Verifica se a quantidade é None
    if quantity_str is None:
        flash('Quantidade inválida.', 'danger')
        return redirect(url_for('view_stock'))
    
    # Tenta converter a quantidade para um número inteiro
    try:
        quantity = int(quantity_str)
    except ValueError:
        flash('Quantidade deve ser um número válido.', 'danger')
        return redirect(url_for('view_stock'))
    
    # Procura o equipamento no banco de dados pelo modelo
    equipment = EquipmentStock.query.filter_by(model=model).first()
    if equipment:
        # Se o equipamento existir, atualiza a quantidade em estoque
        equipment.quantity_in_stock += quantity
        db.session.commit()
        flash('Quantidade atualizada com sucesso!', 'success')
    else:
        # Se o equipamento não existir, cria um novo objeto EquipmentStock e adiciona ao banco de dados
        value = EQUIPMENT_VALUES.get(model, 0.0) 
        new_equipment = EquipmentStock(model=model, quantity_in_stock=quantity)
        db.session.add(new_equipment)
        db.session.commit()
        flash('Equipamento adicionado ao estoque com sucesso!', 'success')
    
    # Redireciona para a página de visualização do estoque após a adição
    return redirect(url_for('view_stock'))

# Rota para retirar os itens do estoque
@app.route('/stock/withdraw', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Admin', 'Inteligência'])  # Verifica as permissões do usuário
def withdraw_from_stock():
    # Recupera o modelo do equipamento e a quantidade do formulário
    model = request.form.get('withdrawal-model')
    quantity_str = request.form.get('withdrawal-quantity_in_stock')
    
    # Verifica se a quantidade é None
    if quantity_str is None:
        flash('Quantidade inválida.', 'danger')
        return redirect(url_for('view_stock'))
    
    # Tenta converter a quantidade para um número inteiro
    try:
        quantity = int(quantity_str)
    except ValueError:
        flash('Quantidade deve ser um número válido.', 'danger')
        return redirect(url_for('view_stock'))
    
    # Procura o equipamento no banco de dados pelo modelo
    equipment = EquipmentStock.query.filter_by(model=model).first()
    if equipment and equipment.quantity_in_stock >= quantity:
        # Se o equipamento existir e houver quantidade suficiente em estoque, atualiza a quantidade em estoque
        equipment.quantity_in_stock -= quantity
        db.session.commit()
        flash('Equipamento removido do estoque com sucesso!', 'success')
    else:
        # Se o equipamento não existir ou não houver quantidade suficiente em estoque, exibe uma mensagem de erro para o usuário
        flash('Quantidade insuficiente no estoque.', 'danger')
    
    # Redireciona para a página de visualização do estoque após a retirada
    return redirect(url_for('view_stock'))

# Rota para o formulário de acompanhamento
@app.route('/activation', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência'])  # Verifica as permissões do usuário
def activation():
    # Cria uma instância do formulário de ativação
    form = ActivationForm()
    
    # Define as opções do campo 'provider' do formulário com base nos provedores do banco de dados
    form.provider.choices = [(p.id, p.name) for p in Provider.query.all()]

    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Cria um novo objeto Activation com os dados do formulário
        activation = Activation(
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            provider_id=form.provider.data,
            plates=form.plates.data,
            agents=form.agents.data,
            equipment_id=form.equipment_id.data,
            initial_km=form.initial_km.data,
            final_km=form.final_km.data,
            toll=form.toll.data
        )
        
        # Adiciona a ativação à sessão do banco de dados
        db.session.add(activation)
        
        # Salva as alterações no banco de dados
        db.session.commit()

        # Registra a ação no histórico
        action = f"Enviou um registro de acompanhamento"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()
        
        # Exibe uma mensagem de sucesso para o usuário
        flash('Acionamento registrado com sucesso!', 'success')
        
        # Redireciona para o formulário de ativação após a submissão
        return redirect(url_for('activation'))

    # Renderiza o template do formulário de ativação com o formulário
    return render_template('activation.html', form=form)

# Rota para a criação de prestador
@app.route('/provider', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência'])  # Verifica as permissões do usuário
def add_provider():
    # Cria uma instância do formulário de prestador
    form = ProviderForm()
    
    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Cria um novo objeto Provider com os dados do formulário
        provider = Provider(
            name=form.name.data,
            km_allowance=form.km_allowance.data,
            hour_allowance=form.hour_allowance.data,
            activation_value=form.activation_value.data,
            km_excess_value=form.km_excess_value.data,
            excess_value=form.excess_value.data
        )
        
        # Adiciona o prestador à sessão do banco de dados
        db.session.add(provider)
        
        # Salva as alterações no banco de dados
        db.session.commit()
        
        # Registra a ação no histórico
        action = f"Criou um novo prestador"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()

        # Exibe uma mensagem de sucesso para o usuário
        flash('Prestador adicionado com sucesso!', 'success')
        
        # Redireciona para a rota de adição de prestador após a submissão
        return redirect(url_for('add_provider'))

    # Renderiza o template do formulário de prestador com o formulário
    return render_template('provider.html', form=form)

@app.route('/providers', methods=['GET'])
@login_required
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência', 'Supervisor'])
def list_providers():
    providers = Provider.query.all()
    return render_template('providers.html', providers=providers)

@app.route('/provider/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência'])
def edit_provider(id):
    provider = Provider.query.get(id)
    form = ProviderEditForm(obj=provider)

    if form.validate_on_submit():
        form.populate_obj(provider)
        db.session.commit()
        
        # Registra a ação no histórico
        action = f"Editou um prestador | {id}"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()
        
        flash('Prestador atualizado com sucesso!', 'success')
        return redirect(url_for('list_providers'))

    return render_template('edit_provider.html', form=form)

@app.route('/provider/<int:id>/delete', methods=['POST'])
@login_required
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência'])
def delete_provider(id):
    provider = Provider.query.get(id)
    db.session.delete(provider)
    db.session.commit()
    
    # Registra a ação no histórico
    action = f"Excluiu um prestador | {id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()
    
    flash('Prestador excluído com sucesso!', 'success')
    return redirect(url_for('list_providers'))

# Rota para a criação de cliente
@app.route('/client', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência'])  # Verifica as permissões do usuário
def add_client():
    # Cria uma instância do formulário de cliente
    form = ClientForm()
    
    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Cria um novo objeto Client com os dados do formulário
        client = Client(
            name=form.name.data,
            km_allowance=form.km_allowance.data,
            hour_allowance=form.hour_allowance.data,
            activation_value=form.activation_value.data,
            km_excess_value=form.km_excess_value.data,
            excess_value=form.excess_value.data
        )
        
        # Adiciona o cliente à sessão do banco de dados
        db.session.add(client)
        
        # Salva as alterações no banco de dados
        db.session.commit()
        
        # Registra a ação no histórico
        action = f"Criou um novo cliente"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()

        # Exibe uma mensagem de sucesso para o usuário
        flash('Cliente adicionado com sucesso!', 'success')
        
        # Redireciona para a rota de adição de cliente após a submissão
        return redirect(url_for('add_client'))

    # Renderiza o template do formulário de cliente com o formulário
    return render_template('client.html', form=form)

@app.route('/clients', methods=['GET'])
@login_required
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência'])
def list_clients():
    clients = Client.query.all()
    return render_template('clients.html', clients=clients)

@app.route('/client/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência'])
def edit_client(id):
    client = Client.query.get(id)
    form = ClientEditForm(obj=client)

    if form.validate_on_submit():
        form.populate_obj(client)
        db.session.commit()
        
        # Registra a ação no histórico
        action = f"Editou um cliente | {id}"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()
        
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('list_clients'))

    return render_template('edit_client.html', form=form)

@app.route('/client/<int:id>/delete', methods=['POST'])
@login_required
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência'])
def delete_client(id):
    client = Client.query.get(id)
    db.session.delete(client)
    db.session.commit()
    
    # Registra a ação no histórico
    action = f"Excluiu um cliente | {id}"
    log = Log(user_id=current_user.username, action=action)
    db.session.add(log)
    db.session.commit()
    
    flash('Cliente excluído com sucesso!', 'success')
    return redirect(url_for('list_clients'))

# Rota para exibição das informações do acompanhamento com os cálculos realizados baseado nos parâmetros definidos pelo prestador e cliente
@app.route('/activation/<int:id>', methods=['GET'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência'])  # Verifica as permissões do usuário
def activation_details(id):
    # Recupera a ativação do banco de dados pelo ID
    activation = Activation.query.get(id)
    
    # Recupera o prestador e o cliente do banco de dados
    provider = Provider.query.get(activation.provider_id)
    client = Client.query.get(activation.client_id) if activation.client_id else None
    
    # Calcula o total de horas da ativação
    total_seconds = (activation.end_time - activation.start_time).total_seconds()
    total_hours = total_seconds / 3600

    # Calcula a permissão de horas do prestador em segundos
    hour_allowance_in_seconds = provider.hour_allowance.hour * 3600 + provider.hour_allowance.minute * 60 + provider.hour_allowance.second
    
    # Calcula as horas excedentes
    excess_hours = max(0, total_hours - hour_allowance_in_seconds / 3600)

    # Calcula o total de km da ativação e os km excedentes
    total_km = activation.final_km - activation.initial_km
    excess_km = max(0, total_km - provider.km_allowance)

    # Calcula o valor total da ativação
    total_value = provider.activation_value + excess_hours * provider.excess_value + excess_km * provider.km_excess_value + activation.toll
    
    # Se o cliente existir, calcula os valores para o cliente
    if client:
        client_hour_allowance_in_seconds = client.hour_allowance.hour * 3600 + client.hour_allowance.minute * 60 + client.hour_allowance.second
        client_excess_hours = max(0, total_hours - client_hour_allowance_in_seconds / 3600)
        client_excess_km = max(0, total_km - client.km_allowance)
        client_total_value = client.activation_value + client_excess_hours * client.excess_value + client_excess_km * client.km_excess_value + activation.client_toll
    else:
        client_excess_hours = client_excess_km = client_total_value = None

    # Formata os valores para ter no máximo duas casas decimais e a data para o formato dd/mm/yyyy hh:mm
    total_km = "{:.0f}".format(total_km) if total_km.is_integer() else "{:.2f}".format(total_km)
    excess_km = "{:.0f}".format(excess_km) if excess_km.is_integer() else "{:.2f}".format(excess_km)
    client_excess_km_formatted = "{:.0f}".format(client_excess_km) if client_excess_km.is_integer() else "{:.2f}".format(client_excess_km)
    total_value = "{:.2f}".format(total_value)
    client_total_value_formatted = "{:.2f}".format(client_total_value)
    toll = "{:.2f}".format(float(activation.toll))
    client_toll = "{:.2f}".format(float(activation.client_toll))
    start_time_formatted = activation.start_time.strftime("%d/%m/%Y %H:%M")
    end_time_formatted = activation.end_time.strftime("%d/%m/%Y %H:%M")
    total_hours_formatted = "{:02d}:{:02d}".format(int(float(total_hours)), int((float(total_hours) * 60) % 60))
    excess_hours_formatted = "{:02d}:{:02d}".format(int(float(excess_hours)), int((float(excess_hours) * 60) % 60))
    client_excess_hours_formatted = "{:02d}:{:02d}".format(int(float(client_excess_hours)), int((float(client_excess_hours) * 60) % 60))

    # Renderiza o template 'activation_details.html' com as informações da ativação, do prestador, do cliente e dos cálculos realizados
    return render_template('activation_details.html', activation=activation, provider=provider, client=client, total_km=total_km, excess_km=excess_km, total_value=total_value, start_time_formatted=start_time_formatted, end_time_formatted=end_time_formatted, toll=toll, total_hours_formatted=total_hours_formatted, excess_hours_formatted=excess_hours_formatted, client_excess_hours_formatted=client_excess_hours_formatted, client_excess_km=client_excess_km_formatted, client_total_value_formatted=client_total_value_formatted, client_toll=client_toll)

# Rota para exibição dos acionamentos
@app.route('/activations', methods=['GET'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência', 'CEO', 'Diretoria'])  # Verifica as permissões do usuário
def list_activations():
    # Recupera todos os acionamentos e clientes do banco de dados
    page = request.args.get('page', 1, type=int)
    
    activations = Activation.query.paginate(page=page, per_page=30)
    clients = Client.query.all()
    
    # Renderiza o template 'activations.html' com os acionamentos e clientes
    return render_template('activations.html', activations=activations, clients=clients, Client=Client, Provider=Provider)

# Rota para edição do acionamento e alteração de status
@app.route('/activation/<int:id>/edit', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência'])  # Verifica as permissões do usuário
def edit_activation(id):
    # Recupera a ativação do banco de dados pelo ID
    activation = Activation.query.get(id)
    
    # Cria uma instância do formulário de edição de ativação com os dados da ativação
    form = ActivationEditForm(obj=activation)
    
    # Define as opções dos campos 'provider' e 'client' do formulário com base nos prestadores e clientes do banco de dados
    form.provider.choices = [(p.id, p.name) for p in Provider.query.all()]
    form.client.choices = [(c.id, c.name) for c in Client.query.all()]

    # Verifica se o formulário foi submetido e validado corretamente
    if form.validate_on_submit():
        # Preenche o objeto ativação com os dados do formulário
        form.populate_obj(activation)
        
        # Atualiza o status da ativação para 'Completo'
        activation.status = 'Completo'
        
        # Atualiza o ID do prestador e do cliente da ativação com base nos dados do formulário
        activation.provider_id = form.provider.data
        activation.client_id = form.client.data
        
        # Salva as alterações no banco de dados
        db.session.commit()
        
        # Registra a ação no histórico
        action = f"Editou um acionamento | {id}"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()

        # Exibe uma mensagem de sucesso para o usuário
        flash('Acionamento atualizado com sucesso!', 'success')
        
        # Redireciona para a página de detalhes da ativação após a edição
        return redirect(url_for('activation_details', id=id))

    # Renderiza o template do formulário de edição de ativação com o formulário e a ativação
    return render_template('edit_activation.html', form=form, activation=activation)

# Rota para exportar um relatório dos acionamentos, baseado no range selecionado
@app.route('/export_activations', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência', 'CEO', 'Diretoria'])  # Verifica as permissões do usuário
def export_activations():
    # Recupera as datas de início e fim do formulário
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    # Converte as datas para objetos datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Obtém todos os acionamentos no intervalo de datas que têm uma data final
    activations = Activation.query.filter(Activation.start_time.between(start_date, end_date), Activation.status == 'Enviado ao Faturamento').all()

    # Cria um novo workbook e uma nova planilha
    wb = Workbook()
    ws = wb.active

    # Adicione os cabeçalhos à planilha
    headers = ['ID', 'Data e Hora Inicial', 'Data e Hora Final', 'Prestador', 'Placas', 'Agentes', 'ID do Equipamento', 'KM Inicial', 'KM Final', 'Pedágio', 'Horas Totais', 'Horas Excedentes', 'KM Total', 'KM Excedente', 'Valor Total', 'Cliente', 'Pedágio Cliente', 'Horas Excedentes Cliente', 'KM Excedente Cliente', 'Valor Total Cliente']
    ws.append(headers)

    for activation in activations:
        provider = Provider.query.get(activation.provider_id)
        client = Client.query.get(activation.client_id) if activation.client_id else None

        # Calcule os valores necessários
        total_seconds = (activation.end_time - activation.start_time).total_seconds()
        total_hours = total_seconds / 3600
        hour_allowance_in_seconds = provider.hour_allowance.hour * 3600 + provider.hour_allowance.minute * 60 + provider.hour_allowance.second
        excess_hours = max(0, total_hours - hour_allowance_in_seconds / 3600)
        total_km = activation.final_km - activation.initial_km
        excess_km = max(0, total_km - provider.km_allowance)
        total_value = provider.activation_value + excess_hours * provider.excess_value + excess_km * provider.km_excess_value + activation.toll

        # Se o cliente existir, calcule os valores para o cliente
        if client:
            client_hour_allowance_in_seconds = client.hour_allowance.hour * 3600 + client.hour_allowance.minute * 60 + client.hour_allowance.second
            client_excess_hours = max(0, total_hours - client_hour_allowance_in_seconds / 3600)
            client_excess_km = max(0, total_km - client.km_allowance)
            client_total_value = client.activation_value + client_excess_hours * client.excess_value + client_excess_km * client.km_excess_value + activation.client_toll
        else:
            client_excess_hours = client_excess_km = client_total_value = None

        # Formate os valores para ter no máximo duas casas decimais e a data para o formato dd/mm/yyyy hh:mm
        total_km = "{:.0f}".format(total_km) if total_km.is_integer() else "{:.2f}".format(total_km)
        excess_km = "{:.0f}".format(excess_km) if excess_km.is_integer() else "{:.2f}".format(excess_km)
        client_excess_km_formatted = "{:.0f}".format(client_excess_km) if client_excess_km and client_excess_km.is_integer() else "{:.2f}".format(client_excess_km) if client_excess_km else None
        total_value = "R$ {:.2f}".format(total_value)
        client_total_value_formatted = "R$ {:.2f}".format(client_total_value) if client_total_value else None
        toll = "R$ {:.2f}".format(float(activation.toll))
        client_toll = "R$ {:.2f}".format(float(activation.client_toll)) if activation.client_toll else None
        start_time_formatted = activation.start_time.strftime("%d/%m/%Y %H:%M")
        end_time_formatted = activation.end_time.strftime("%d/%m/%Y %H:%M")
        total_hours_formatted = "{:02d}:{:02d}".format(int(float(total_hours)), int((float(total_hours) * 60) % 60))
        excess_hours_formatted = "{:02d}:{:02d}".format(int(float(excess_hours)), int((float(excess_hours) * 60) % 60))
        client_excess_hours_formatted = "{:02d}:{:02d}".format(int(float(client_excess_hours)), int((float(client_excess_hours) * 60) % 60)) if client_excess_hours else None

        # Adicione os dados à planilha
        data = [activation.id, start_time_formatted, end_time_formatted, provider.name, activation.plates, activation.agents, activation.equipment_id, activation.initial_km, activation.final_km, toll, total_hours_formatted, excess_hours_formatted, total_km, excess_km, total_value, client.name if client else None, client_toll, client_excess_hours_formatted, client_excess_km_formatted, client_total_value_formatted]
        ws.append(data)

    # Salve o workbook em um objeto BytesIO
    excel_data = BytesIO()
    wb.save(excel_data)

    # Crie uma resposta com o arquivo Excel
    response = make_response(excel_data.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=activations.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return response

# Rota para alterar o status do acionamento
@app.route('/activation/<int:id>/send_to_billing', methods=['POST'])
@login_required  # Requer que o usuário esteja autenticado
@check_permissions(['Supervisor', 'Admin', 'Inteligência'])  # Verifica as permissões do usuário
def send_to_billing(id):
    # Recupera a ativação do banco de dados pelo ID
    activation = Activation.query.get(id)
    
    # Verifica se o status da ativação é 'Completo'
    if activation.status == 'Completo':
        # Atualiza o status da ativação para 'Enviado ao Faturamento'
        activation.status = 'Enviado ao Faturamento'
        
        # Salva as alterações no banco de dados
        db.session.commit()

        # Registra a ação no histórico
        action = f"Enviou um acionamento ao Faturamento | {id}"
        log = Log(user_id=current_user.username, action=action)
        db.session.add(log)
        db.session.commit()

        # Exibe uma mensagem de sucesso para o usuário
        flash('Acionamento enviado ao faturamento com sucesso!', 'success')
    else:
        # Se o status da ativação não for 'Completo', exibe uma mensagem de erro para o usuário
        flash('O acionamento precisa estar com status "Completo" para ser enviado ao faturamento.', 'error')
    
    # Redireciona para a página de detalhes da ativação após a alteração do status
    return redirect(url_for('activation_details', id=id))

@app.route('/financial', methods=['GET', 'POST'])
@login_required
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência', 'CEO', 'Diretoria'])
def financial():
    if request.method == 'POST':
        # Obtém as datas do formulário
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        status = request.form.get('status')

        # Cria uma consulta base
        query = Activation.query

        # Se as datas foram especificadas, filtra por data
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Activation.start_time.between(start_date, end_date))

        # Se o status foi especificado, filtra por status
        if status:
            query = query.filter(Activation.status == status)

        # Obtém todos os acionamentos que correspondem aos critérios de filtro
        activations = query.all()
    else:
        # Se a solicitação é GET, obtém todos os acionamentos
        activations = Activation.query.all()
        
    with db.session.no_autoflush:
        for activation in activations:
            provider = Provider.query.get(activation.provider_id)
            client = Client.query.get(activation.client_id) if activation.client_id else None

            # Calcule os valores necessários
            if activation.start_time is not None and activation.end_time is not None:
                total_seconds = (activation.end_time - activation.start_time).total_seconds()
                total_hours = total_seconds / 3600
            else:
                total_seconds = total_hours = None
            hour_allowance_in_seconds = provider.hour_allowance.hour * 3600 + provider.hour_allowance.minute * 60 + provider.hour_allowance.second
            if total_hours is not None:
                excess_hours = max(0, total_hours - hour_allowance_in_seconds / 3600)
            else:
                excess_hours = None
            if activation.final_km is not None and activation.initial_km is not None:
                total_km = activation.final_km - activation.initial_km
            else:
                total_km = None
            if total_km is not None and provider.km_allowance is not None:
                excess_km = max(0, total_km - provider.km_allowance)
            else:
                excess_km = None

            if provider.activation_value is not None and excess_hours is not None and provider.excess_value is not None and excess_km is not None and provider.km_excess_value is not None and activation.toll is not None:
                total_value = provider.activation_value + excess_hours * provider.excess_value + excess_km * provider.km_excess_value + activation.toll
            else:
                total_value = None

            # Se o cliente existir, calcula os valores para o cliente
            if client:
                client_hour_allowance_in_seconds = client.hour_allowance.hour * 3600 + client.hour_allowance.minute * 60 + client.hour_allowance.second
                client_excess_hours = max(0, total_hours - client_hour_allowance_in_seconds / 3600)
                client_excess_km = max(0, total_km - client.km_allowance)
                client_total_value = client.activation_value + client_excess_hours * client.excess_value + client_excess_km * client.km_excess_value + activation.client_toll
            else:
                client_excess_hours = client_excess_km = client_total_value = None
                
            # Formate os valores para ter no máximo duas casas decimais e a data para o formato dd/mm/yyyy hh:mm
            activation.total_km = "{:.0f}".format(total_km) if total_km is not None and total_km.is_integer() else "{:.2f}".format(total_km) if total_km is not None else None
            activation.excess_km = "{:.0f}".format(excess_km) if excess_km is not None and excess_km.is_integer() else "{:.2f}".format(excess_km) if excess_km is not None else None
            activation.client_excess_km_formatted = "{:.0f}".format(client_excess_km) if client_excess_km is not None and client_excess_km.is_integer() else "{:.2f}".format(client_excess_km) if client_excess_km is not None else None
            activation.total_value = "R$ {:.2f}".format(total_value) if total_value is not None else None
            activation.client_total_value_formatted = "R$ {:.2f}".format(client_total_value) if client_total_value is not None else None
            activation.toll = "R$ {:.2f}".format(activation.toll) if activation.toll is not None else None
            activation.client_toll = "R$ {:.2f}".format(activation.client_toll) if activation.client_toll is not None else None
            activation.start_time_formatted = activation.start_time.strftime("%d/%m/%Y %H:%M") if activation.start_time is not None else None
            activation.end_time_formatted = activation.end_time.strftime("%d/%m/%Y %H:%M") if activation.end_time is not None else None
            activation.total_hours_formatted = "{:02d}:{:02d}".format(int(float(total_hours)), int((float(total_hours) * 60) % 60)) if total_hours is not None else None
            activation.excess_hours_formatted = "{:02d}:{:02d}".format(int(float(excess_hours)), int((float(excess_hours) * 60) % 60)) if excess_hours is not None else None
            activation.client_excess_hours_formatted = "{:02d}:{:02d}".format(int(float(client_excess_hours)), int((float(client_excess_hours) * 60) % 60)) if client_excess_hours is not None else None

        return render_template('financial.html', activations=activations, Client=Client, Provider=Provider)

@app.route('/update_status/<int:activation_id>', methods=['POST'])
@login_required
@check_permissions(['Acompanhamento', 'Admin', 'Inteligência', 'CEO', 'Diretoria'])
def update_status(activation_id):
    # Obtém o acionamento pelo ID
    activation = Activation.query.get(activation_id)

    # Atualiza o status
    activation.status = 'Faturado'

    # Salva as alterações no banco de dados
    db.session.commit()

    # Redireciona o usuário de volta para a página financeira
    return redirect(url_for('financial'))