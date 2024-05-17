#pdf_sales.py
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def general_pdf(data, app):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2, bottomMargin=0, leftMargin=10, rightMargin=10)
    styles = getSampleStyleSheet()
    
    # Criando um novo estilo para um texto com tamanho de fonte menor
    styles.add(ParagraphStyle(name='SmallText', parent=styles['Normal'], fontSize=10))

    elements = []

    # Cabeçalho
    logo_path = os.path.join(app.root_path, "static", "img/logo-golden.png")
    logo = Image(logo_path, width=1.5*inch, height=1.5*inch)
    logo.hAlign = 'CENTER'  # Centralizando o logo
    logo.vAlign = 'TOP'  # Ajustando o logo para o topo
    elements.append(logo)
    
    header_text = f"{data['client']} - {data['id']}"
    header_paragraph = Paragraph(header_text, styles['Heading1'])
    header_paragraph.alignment = 1  # Centralizando o texto do cabeçalho
    elements.append(header_paragraph)
    
    elements.append(Spacer(1, 12))

    # Corpo
    elements.append(Paragraph(f"<b>Data:</b> {data['date_completed']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>CNPJ:</b> {data['cnpj']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Início de Contrato:</b> {data['contract_start']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Vigência:</b> {data['vigency']}", styles['BodyText']))
    
    reason_text = f"<b>Motivo:</b> {data['reason']}"
    if data['reason'] == 'Isca Fast':
        reason_text += f" | <b>Local de Saída:</b> {data['location']}"
    if data['reason'] == 'Manutenção':
        reason_text += f" | <b>Protocolo de Manutenção:</b> {data['maintenance_number']}"
    elements.append(Paragraph(reason_text, styles['BodyText']))

    elements.append(Paragraph(f"<b>Cliente:</b> {data['client']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Comercial:</b> {data['sales_rep']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Contrato:</b> {data['contract_type']}", styles['BodyText']))

    shipping_text = f"<b>Envio:</b> {data['shipping']}"
    if data['shipping'] == 'Motoboy':
        shipping_text += f" | <b>Taxa de Entrega:</b> R$ {data['delivery_fee']}"
    elements.append(Paragraph(shipping_text, styles['BodyText']))

    elements.append(Paragraph(f"<b>Endereço:</b> {data['address']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>A/C:</b> {data['contact_person']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>E-mail:</b> {data['email']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Telefone de Contato:</b> {data['phone']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Quantidade:</b> {data['quantity']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Modelo:</b> {data['model']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Customização:</b> {data['customization']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>TP:</b> {data['tp']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Carregador:</b> {data['charger']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Cabo:</b> {data['cable']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Tipo de Fatura:</b> {data['invoice_type']}", styles['BodyText']))
    final_value = f"<b>Valor Unitário:</b> R$ {data['value']} | <b>Valor Total:</b> R$ {data['total_value']}"
    elements.append(Paragraph(final_value, styles['BodyText']))
    elements.append(Paragraph(f"<b>Forma de Pagamento:</b> {data['payment_method']}", styles['BodyText']))
    elements.append(Paragraph(f"<b>Observações:</b> {data['observations']}", styles['BodyText']))
    
    elements.append(Spacer(1, 12))
    
    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data