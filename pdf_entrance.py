import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO

def add_header_and_title(elements, app):
    # Cabeçalho
    logo_path = os.path.join(app.root_path, "static", "img/logo-golden.png")
    logo = Image(logo_path, width=1.5*inch, height=1.5*inch)

    # QR Code
    qr_code_path = os.path.join(app.root_path, "static", "img/qrcode.png")
    qr_code = Image(qr_code_path, width=100, height=100)  # Ajuste o tamanho conforme necessário

    # Criando uma tabela com uma única linha e duas colunas para posicionar o logo e o QR code lado a lado
    header_table_data = [[logo, qr_code]]
    header_table = Table(header_table_data, colWidths=[1.5*inch, 100])
    elements.append(header_table)

    # Adiciona um espaço entre o header e o título
    elements.append(Spacer(1, 12))

    # Título
    title_text = "PROTOCOLO DE ENTRADA"
    title_paragraph = Paragraph(title_text, styles['Title'])
    title_paragraph.alignment = 1
    elements.append(title_paragraph)
    elements.append(Spacer(1, 3))

def add_request_info(elements, entrance):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenteredBodyText', parent=styles['BodyText'], alignment=1))

    # Informações da entrada
    first_line = f"<b>ID da Entrada:</b> {entrance.id} | <b>Data:</b> {entrance.date}"
    second_line = f"<b>Cliente:</b> {entrance.client} | <b>Tipo de Entrada:</b> {entrance.entrance_type}"
    third_line = f"<b>Modelo:</b> {entrance.model} | <b>Customização:</b> {entrance.customization}"
    fourth_line = f"<b>Tipo de Recebimento:</b> {entrance.type_of_receipt}"
    if entrance.type_of_receipt == 'Entregue na base':
        fourth_line += f" | <b>Nome do Entregador:</b> {entrance.recipients_name}"
    elif entrance.type_of_receipt == 'Retirado no cliente':
        fourth_line += f" | <b>Retirado por:</b> {entrance.withdrawn_by}"

    elements.append(Paragraph(first_line, styles['CenteredBodyText']))
    elements.append(Paragraph(second_line, styles['CenteredBodyText']))
    elements.append(Paragraph(third_line, styles['CenteredBodyText']))
    elements.append(Paragraph(fourth_line, styles['CenteredBodyText']))
    elements.append(Spacer(1, 12))  # Espaço entre as informações e os números dos equipamentos

def add_equipment_numbers(elements, equipment_numbers):
    # Convertendo para inteiros e ordenando numericamente
    equipment_numbers = sorted(map(int, (num.strip() for num in equipment_numbers.split(';') if num.strip())))

    # Dividindo os números em grupos de 8
    equipment_grid = [equipment_numbers[i:i+8] for i in range(0, len(equipment_numbers), 8)]

    # Adicionando subtítulo
    subtitle_text = "IDS DOS EQUIPAMENTOS"
    subtitle_paragraph = Paragraph(subtitle_text, styles['Title'])
    subtitle_paragraph.alignment = 1  # Centralizando o subtítulo
    elements.append(subtitle_paragraph)
    elements.append(Spacer(1, 6))  # Espaço entre o subtítulo e a tabela

    # Criando a tabela para os números dos equipamentos
    equipment_table_data = []
    for group in equipment_grid:
        row = [str(num) for num in group]  # Convertendo os números para strings
        equipment_table_data.append(row)

    # Adicionando a tabela à lista de elementos
    equipment_table = Table(equipment_table_data)
    elements.append(equipment_table)
    elements.append(Spacer(1, inch))  # Adiciona um espaço entre os números e o footer

def generate_entrance_pdf(entrance, app):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2, bottomMargin=1 * inch, leftMargin=10, rightMargin=10)
    global styles
    styles = getSampleStyleSheet()

    elements = []

    add_header_and_title(elements, app)
    add_request_info(elements, entrance)
    add_equipment_numbers(elements, entrance.equipment_numbers)
    
    # Cria o PDF
    doc.build(elements)

    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data