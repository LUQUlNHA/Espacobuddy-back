# Importa os módulos necessários do Flask para criar a API e lidar com requisições/respostas
from flask import Flask, request, jsonify

# Importa o driver para PostgreSQL
import psycopg2
from psycopg2 import sql  # Usado para construir queries seguras e dinâmicas

# Importa para carregar variáveis de ambiente do arquivo .env
from dotenv import load_dotenv
import os  # Usado para acessar variáveis de ambiente

# Carrega as variáveis definidas no arquivo .env (como DB_HOST, DB_USER, etc)
load_dotenv()

# Inicializa a aplicação Flask
app = Flask(__name__)

# Importa e configura o CORS para aceitar requisições de qualquer origem
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Função responsável por estabelecer conexão com o banco PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),        # Endereço do banco
        database=os.getenv('DB_NAME'),    # Nome do banco
        user=os.getenv('DB_USER'),        # Usuário
        password=os.getenv('DB_PASSWORD') # Senha
    )

# Rota para inserir registros dinamicamente em qualquer tabela
@app.route('/api/register', methods=['POST'])
def dynamic_register():
    try:
        # Pega os dados JSON enviados na requisição
        data = request.get_json()

        # Recupera o nome da tabela e os campos a serem inseridos
        table_name = data.get('table_name')
        fields_data = data.get('fields')

        # Validação: verifica se ambos foram enviados
        if not table_name or not fields_data:
            return jsonify({'error': 'Nome da tabela e campos são obrigatórios!'}), 400

        # Abre conexão com o banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        # Cria a string com os nomes das colunas
        columns = ', '.join(fields_data.keys())

        # Cria os placeholders (%s) para valores
        values = ', '.join(['%s'] * len(fields_data))

        # Monta a query SQL de inserção de forma segura usando psycopg2.sql
        insert_query = sql.SQL("""
            INSERT INTO {table} ({fields}) VALUES ({values})
        """).format(
            table=sql.Identifier(table_name),       # Nome da tabela (evita SQL injection)
            fields=sql.SQL(columns),                # Nomes das colunas
            values=sql.SQL(values)                  # Placeholders dos valores
        )

        # Executa a query passando os valores na mesma ordem dos campos
        cursor.execute(insert_query, tuple(fields_data.values()))
        conn.commit()  # Aplica a transação no banco

        # Retorna sucesso com status 201 (Created)
        return jsonify({'message': 'Registro inserido com sucesso!'}), 201

    except Exception as e:
        # Em caso de erro, retorna o erro em formato JSON com status 500 (Erro interno)
        return jsonify({'error': str(e)}), 500

    finally:
        # Garante que o cursor e conexão serão fechados (se existirem)
        try:
            cursor.close()
            conn.close()
        except:
            pass

# Captura globalmente qualquer erro HTTP 500 que não tenha sido tratado
@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

# Ponto de entrada da aplicação quando executada diretamente
if __name__ == '__main__':
    app.config['ENV'] = 'production'                # Define o ambiente como produção
    app.run(host='0.0.0.0', port=5000, threaded=True)  # Executa o servidor na porta 5000 acessível externamente
