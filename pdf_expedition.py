#pdf_expedition.py
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
    title_text = "PROTOCOLO DE ENTREGA"
    title_paragraph = Paragraph(title_text, styles['Title'])
    title_paragraph.alignment = 1
    elements.append(title_paragraph)
    elements.append(Spacer(1, 3))

def add_request_info(elements, data):

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenteredBodyText', parent=styles['BodyText'], alignment=1))
    # Informações da requisição
    first_line = f"<b>Pedido:</b> {data['id']} | <b>Contrato:</b> {data['contract_type']} | <b>Data:</b> {data['date_completed']}"
    second_line = f"<b>Cliente:</b> {data['client']} | <b>Quantidade:</b> {data['quantity']}"
    third_line = f"<b>Modelo:</b> {data['model']} | <b>Customização:</b> {data['customization']} | <b>Carregadores:</b> {data['chargers']} | <b>Cabos:</b> {data['cables']}"
    elements.append(Paragraph(first_line, styles['CenteredBodyText']))
    elements.append(Paragraph(second_line, styles['CenteredBodyText']))
    elements.append(Paragraph(third_line, styles['CenteredBodyText']))
    elements.append(Paragraph(f"<b>Endereço:</b> {data['address']}", styles['CenteredBodyText']))
    elements.append(Paragraph(f"<b>A/C:</b> {data['ac']}", styles['CenteredBodyText']))
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

def add_footer(canvas, doc):
    # Footer
    footer_text = [
        ["Nome:", "_______________", "RG:", "_______________", "CPF:", "_______________"],
        ["Data:", "_______________", "Hora:", "_______________", "Assinatura:", "_______________"]
    ]

    footer_table = Table(footer_text, colWidths=[80, 120, 80, 120, 80, 120])

    footer_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Adicione linhas de grade
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinhe todo o texto à esquerda
    ]))

    # Define a posição do footer
    footer_x = 5
    footer_y = 10
    footer_table.wrapOn(canvas, 0, 0)
    footer_table.drawOn(canvas, footer_x, footer_y)

def generate_expedition_pdf(data, app):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2, bottomMargin=1 * inch, leftMargin=10, rightMargin=10)
    global styles
    styles = getSampleStyleSheet()

    elements = []

    add_header_and_title(elements, app)
    add_request_info(elements, data)
    add_equipment_numbers(elements, data['equipment_numbers'])
    
    # Cria o PDF
    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)

    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
