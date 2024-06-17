import sqlite3
import pandas as pd
import openpyxl

# Conecte-se ao banco de dados SQLite
conn = sqlite3.connect('instance/site.db')

# Dicionário mapeando nomes de tabelas para nomes de arquivos CSV
table_to_csv = {
    'entrance': 'entradas.csv',
    'reports': 'manutenções.csv',
    'sales_request': 'requisições.csv'
}

# Dicionário mapeando nomes de arquivos CSV para nomes de arquivos Excel
csv_to_excel = {
    'entradas.csv': 'entradas-final.xlsx',
    'manutenções.csv': 'manutenções-final.xlsx',
    'requisições.csv': 'requisiçoes-final.xlsx'
}

for table, csv_file in table_to_csv.items():
    # Execute a consulta SQL para extrair os dados
    query = f"SELECT * FROM {table}"
    df = pd.read_sql_query(query, conn)

    # Exporte os dados para um arquivo CSV com codificação UTF-8
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')

    # Abra o arquivo Excel correspondente e salve-o para atualizá-lo
    excel_file = csv_to_excel[csv_file]
    wb = openpyxl.load_workbook(excel_file)
    wb.save(excel_file)

# Feche a conexão com o banco de dados
conn.close()