import sqlite3
import pandas as pd

conn = sqlite3.connect('site.db')

table_to_csv = {
    'entrance': 'entradas.csv',
    'reports': 'manutenções.csv',
    'sales_request': 'requisições.csv'
}

for table, csv_file in table_to_csv.items():
    query = f"SELECT * FROM {table}"
    df = pd.read_sql_query(query, conn)

    df.to_csv(csv_file, index=False, encoding='utf-8')

conn.close()