#pdf_maintenance.py
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, TableStyle, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

def generate_pdf(data, app):
    agora = datetime.now()

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
    
    header_text = f"{data['client_name']} - {data['id']}"
    header_paragraph = Paragraph(header_text, styles['Heading1'])
    header_paragraph.alignment = 1  # Centralizando o texto do cabeçalho
    elements.append(header_paragraph)
    
    elements.append(Spacer(1, 12))

    # Corpo
    elements.append(Paragraph(f"<b>Data e Hora:</b> {data['date_completed']}", styles['BodyText']))
    
    elements.append(Paragraph(f"<b>Motivo:</b> {data['reason']}", styles['BodyText']))
    
    modelo_customizacao = f"<b>Modelo:</b> {data['model']} | <b>Customização:</b> {data['customization']}"
    elements.append(Paragraph(modelo_customizacao, styles['BodyText']))
    
    elements.append(Paragraph(f"<b>Número do Equipamento:</b> {data['equipment_number']}", styles['BodyText']))
    
    elements.append(Paragraph(f"<b>Faturamento:</b> {data['billing']}", styles['BodyText']))
    
    elements.append(Paragraph(f"<b>Tipo de Problema:</b> {data['problem_type']}", styles['BodyText']))
    
    elements.append(Spacer(1, 12))
    
    # Lendo o conteúdo dos arquivos txt de acordo com o tipo de problema
    tipo_problema = data['problem_type']
    tipo_problema_texts = {
        'Oxidação': "oxidação.txt",
        'Placa danificada': "placa_danificada.txt",
        'Placa danificada sem custo': "placa_danificada_sem_custo.txt",
        'USB danificado': "usb_danificado.txt",
        'USB danificado sem custo': "usb_danificado_sem_custo.txt",
        'Botão de acionamento danificado': "botao_acionamento.txt",
        'Botão de acionamento danificado sem custo': "botao_acionamento_sem_custo.txt",
        'Antena LoRa danificada': "antena_lora.txt",
        'Sem problemas identificados': "sem_problema_identificado.txt",
    }
    
    if tipo_problema in tipo_problema_texts:
        file_path = os.path.join(app.root_path, "static/textos", tipo_problema_texts[tipo_problema])
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
            elements.append(Paragraph(text_content, styles['SmallText']))
        
    if data['photos']:
        images = []
        for filename in data['photos']:
            photo_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
            with open(photo_path, 'rb') as file:
                img = Image(file, width=2.5*inch, height=1.25*inch)
                images.append(img)
        
        elements.append(Spacer(1, 12))
        img_table = create_image_table(images)
        elements.append(img_table)

    # Tratativa
    elements.append(Paragraph(f"<b>Tratativa:</b> {data['treatment']}", styles['BodyText']))
    
    elements.append(Spacer(1, 12))
    
    # Adicionando a Tratativa
    tratativas = data['treatment']
    tratativas_texts = {
        'Oxidação': """
            <b>Sobre a Manutenção Realizada:</b><br/>
            Para resolver o problema do equipamento, foram realizadas as tratativas necessárias e alguns testes posteriores, porém, sem sucesso, sendo assim será necessária a troca do dispositivo.<br/><br/>
            <i>Atenciosamente,</i><br/>
            Laboratório Técnico. 
        """,
        'Placa danificada': """
            <b>Sobre a Manutenção Realizada:</b><br/>
            Para resolver o problema do equipamento, foram realizadas as tratativas necessárias e alguns testes posteriores, porém, sem sucesso, sendo assim será necessária a troca do dispositivo.<br/><br/>
            <i>Atenciosamente,</i><br/>
            Laboratório Técnico
        """,
        'USB danificado': """
            <b>Sobre a Manutenção Realizada:</b><br/>
            Para resolver o problema do equipamento, foram realizadas as tratativas necessárias e alguns testes posteriores, porém, sem sucesso, sendo assim será necessária a troca do dispositivo.<br/><br/>
            <i>Atenciosamente,</i><br/>
            Laboratório Técnico.
        """,
        'Botão de acionamento danificado': """
            <b>Sobre a Manutenção Realizada:</b><br/>
            Diante deste diagnóstico e após as análises, afirmamos que será necessário a troca do dispositivo.<br/><br/>
            <i>Atenciosamente,</i><br/>
            Laboratório Técnico
        """,
        'Antena LoRa danificada': """
            <b>Sobre a Manutenção Realizada:</b><br/>
            Diante deste diagnóstico e após as tratativas, afirmamos que será necessário a troca do dispositivo.<br/><br/>
            <i>Atenciosamente,</i><br/>
            Laboratório Técnico
        """,
        'Sem problemas identificados': """
            <b>Sobre a Manutenção Realizada:</b><br/>
            Gostaríamos de informar que concluímos com sucesso as manutenções necessárias no equipamento que nos foi confiado para reparo. Após uma análise cuidadosa, identificamos e corrigimos os problemas que estavam impactando o seu funcionamento adequado.<br/><br/>
            <i>Atenciosamente,</i><br/>
            Laboratório Técnico. 
        """
    }
    
    if tratativas in tratativas_texts:
        tratativa_text = tratativas_texts[tratativas]
        tratativa_paragraph = Paragraph(tratativa_text, styles['SmallText'])
        elements.append(tratativa_paragraph)

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

# Função para criar a grade de fotos
def create_image_table(images, max_col=3):
    table_data = []
    row = []
    for img in images:
        if len(row) == max_col:
            table_data.append(row)
            row = []
        row.append(img)
    if row:
        table_data.append(row)
    
    img_table = Table(table_data)
    img_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))

    return img_table