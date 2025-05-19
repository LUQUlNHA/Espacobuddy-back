from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "https://urban-eden.com.br"}})
CORS(app, resources={r"/*": {"origins": "*"}})

# Função para estabelecer a conexão com o banco de dados PostgreSQL
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

# Rota para deletar os dados de uma tabela específica com uma cláusula WHERE


@app.route('/api/delete', methods=['DELETE'])
def delete_from_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    table_name = request.args.get('table_name')
    filters = {key: value for key, value in request.args.items()
               if key != 'table_name'}

    if not table_name:
        return jsonify({'error': 'Parâmetro "table_name" é obrigatório.'}), 400

    if not filters:
        return jsonify({'error': 'É necessário fornecer ao menos uma condição na cláusula WHERE.'}), 400

    try:
        where_clause = build_where_clause(filters)
        query = f"DELETE FROM {table_name}{where_clause}"
        cursor.execute(query, tuple(filters.values()))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Nenhum dado foi deletado. Verifique os filtros.'}), 404

        return jsonify({'message': 'Registro(s) deletado(s) com sucesso.'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.config['ENV'] = 'production'
    app.run(host='0.0.0.0', port=5004, threaded=True)
