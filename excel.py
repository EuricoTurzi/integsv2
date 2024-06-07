from openpyxl import Workbook
from models import Activation, Provider
from app import app  # Importe sua instância de aplicação Flask

# Crie um contexto de aplicação
with app.app_context():
    # Crie um novo workbook e uma nova planilha
    wb = Workbook()
    ws = wb.active

    # Adicione os cabeçalhos à planilha
    headers = ['ID', 'Data e Hora Inicial', 'Data e Hora Final', 'Prestador', 'Placas', 'Agentes', 'ID do Equipamento', 'KM Inicial', 'KM Final', 'Pedágio', 'Horas Totais', 'Horas Excedentes', 'KM Total', 'KM Excedente', 'Valor Total']
    ws.append(headers)

    # Obtenha todos os acionamentos
    activations = Activation.query.all()

    for activation in activations:
        provider = Provider.query.get(activation.provider_id)

        # Calcule os valores necessários
        total_seconds = (activation.end_time - activation.start_time).total_seconds()
        total_hours = total_seconds / 3600
        hour_allowance_in_seconds = provider.hour_allowance.hour * 3600 + provider.hour_allowance.minute * 60 + provider.hour_allowance.second
        excess_hours = max(0, total_hours - hour_allowance_in_seconds / 3600)
        total_km = activation.final_km - activation.initial_km
        excess_km = max(0, total_km - provider.km_allowance)
        total_value = provider.activation_value + excess_hours * provider.excess_value + excess_km * provider.km_excess_value + activation.toll
        
        # Formatar os valores para ter no máximo duas casas decimais e a data para o formato dd/mm/yyyy hh:mm
        total_km = "{:.0f}".format(total_km) if total_km.is_integer() else "{:.2f}".format(total_km)
        excess_km = "{:.0f}".format(excess_km) if excess_km.is_integer() else "{:.2f}".format(excess_km)
        total_value = "{:.2f}".format(total_value)
        toll = "{:.2f}".format(float(activation.toll))
        start_time_formatted = activation.start_time.strftime("%d/%m/%Y %H:%M")
        end_time_formatted = activation.end_time.strftime("%d/%m/%Y %H:%M")
        total_hours_formatted = "{:02d}:{:02d}".format(int(float(total_hours)), int((float(total_hours) * 60) % 60))
        excess_hours_formatted = "{:02d}:{:02d}".format(int(float(excess_hours)), int((float(excess_hours) * 60) % 60))

        # Adicione os dados à planilha
        data = [activation.id, activation.start_time, activation.end_time, provider.name, activation.plates, activation.agents, activation.equipment_id, activation.initial_km, activation.final_km, activation.toll, total_hours, excess_hours, total_km, excess_km, total_value]
        ws.append(data)

    # Salve o workbook
    wb.save('activations.xlsx')
