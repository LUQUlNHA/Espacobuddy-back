from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

def get_db_connection():
    connection = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return connection

# Função para construir a cláusula WHERE dinâmica
def build_where_clause(filters):
    where_clause = ""
    if filters:
        where_clause = " WHERE " + \
            " AND ".join([f"{key} = %s" for key in filters.keys()])
    return where_clause

# Rota para listar os dados de uma tabela específica com chaves estrangeiras

@app.route('/api/list', methods=['GET'])
def list_table_and_foreign_keys():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Parâmetros de consulta
    table_name = request.args.get('table_name')
    filters = {key: value for key, value in request.args.items()
               if key != 'table_name'}

    if not table_name:
        return jsonify({'error': 'Parâmetro "table_name" é obrigatório.'}), 400

    try:
        # Construir a cláusula WHERE com os filtros, se fornecidos
        where_clause = build_where_clause(filters)

        # Consulta para obter os dados da tabela com o filtro WHERE, se houver
        query = f"SELECT * FROM {table_name}{where_clause}"
        cursor.execute(query, tuple(filters.values()))
        table_data = cursor.fetchall()

        # Armazena os nomes das colunas da consulta principal antes de executar outras queries
        main_columns = [desc[0] for desc in cursor.description]

        if not table_data:
            return jsonify({'error': f'Nenhum dado encontrado para a tabela {table_name}'}), 404

        # Agora, vamos obter os valores relacionados através das chaves estrangeiras
        fk_query = """
            SELECT
                kcu.column_name AS column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM
                information_schema.key_column_usage kcu
            JOIN
                information_schema.constraint_column_usage ccu
                ON kcu.constraint_name = ccu.constraint_name
            WHERE
                kcu.table_schema = 'public' AND kcu.table_name = %s
        """
        cursor.execute(fk_query, (table_name,))
        foreign_keys = cursor.fetchall()

        # Vamos usar as informações sobre as chaves estrangeiras para fazer JOINs
        foreign_data = {}
        for fk in foreign_keys:
            column_name = fk[0]
            foreign_table_name = fk[1]
            foreign_column_name = fk[2]

            # Consultar os valores completos da tabela relacionada pela chave estrangeira
            join_query = f"""
                SELECT {foreign_table_name}.* 
                FROM {foreign_table_name}
                WHERE {foreign_table_name}.{foreign_column_name} IN (
                    SELECT {table_name}.{column_name} FROM {table_name}
                )
            """
            cursor.execute(join_query)
            foreign_values = cursor.fetchall()

            # Verifique se há dados antes de tentar acessar
            if foreign_values:
                # Nomes das colunas da tabela relacionada
                column_names = [desc[0] for desc in cursor.description]
                foreign_data[column_name] = {
                    "foreign_table_name": foreign_table_name,
                    "columns": column_names,
                    "values": foreign_values
                }
            else:
                foreign_data[column_name] = {"error": "No foreign data found"}

        # Preparando a resposta utilizando as colunas da consulta principal
        response = {
            'table': table_name,
            'data': [],
            'foreign_values': foreign_data
        }

        for row in table_data:
            row_data = {}
            for idx, col_name in enumerate(main_columns):
                if idx < len(row):
                    row_data[col_name] = row[idx]
            response['data'].append(row_data)

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.config['ENV'] = 'production'
    app.run(host='0.0.0.0', port=5003, threaded=True)
