from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Função para estabelecer a conexão com o banco de dados
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

# Rota para registro dinâmico
@app.route('/api/register', methods=['POST'])
def dynamic_register():
    try:
        data = request.get_json()

        table_name = data.get('table_name')
        fields_data = data.get('fields')

        if not table_name or not fields_data:
            return jsonify({'error': 'Nome da tabela e campos são obrigatórios!'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        columns = ', '.join(fields_data.keys())
        values = ', '.join(['%s'] * len(fields_data))

        insert_query = sql.SQL("""
            INSERT INTO {table} ({fields}) VALUES ({values})
        """).format(
            table=sql.Identifier(table_name),
            fields=sql.SQL(columns),
            values=sql.SQL(values)
        )

        cursor.execute(insert_query, tuple(fields_data.values()))
        conn.commit()

        return jsonify({'message': 'Registro inserido com sucesso!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

# ⛔️ Novo! Captura erros 500 que escaparem:
@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    app.config['ENV'] = 'production'
    app.run(host='0.0.0.0', port=5000, threaded=True)
