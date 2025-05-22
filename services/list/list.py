# Importação de bibliotecas para servidor, banco de dados, CORS e variáveis de ambiente
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv
import os

# Carrega variáveis do arquivo .env (ex: credenciais do banco de dados)
load_dotenv()

# Criação da aplicação Flask
app = Flask(__name__)

# Ativa o CORS para permitir requisições de diferentes origens (aqui está liberado para todas)
CORS(app, resources={r"/*": {"origins": "*"}})

# Função de conexão com o banco de dados PostgreSQL
def get_db_connection():
    """
    Retorna uma nova conexão com o banco PostgreSQL usando variáveis de ambiente.
    SRP (Responsabilidade Única): esta função só trata da conexão.
    """
    connection = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return connection

# Função auxiliar para montar cláusulas WHERE dinâmicas a partir dos filtros recebidos
def build_where_clause(filters):
    """
    Constrói uma cláusula WHERE dinâmica a partir de um dicionário de filtros.
    OCP (Aberto para Extensão): pode ser melhorada para suportar LIKE, >, < etc.
    """
    where_clause = ""
    if filters:
        where_clause = " WHERE " + \
            " AND ".join([f"{key} = %s" for key in filters.keys()])
    return where_clause

# Endpoint principal da API: lista dados de uma tabela com suporte a filtros e chaves estrangeiras
@app.route('/api/list', methods=['GET'])
def list_table_and_foreign_keys():
    """
    Endpoint que retorna dados de uma tabela específica e, se houver, dados das tabelas referenciadas por chaves estrangeiras.
    """

    # Conexão com o banco
    conn = get_db_connection()
    cursor = conn.cursor()

    # Coleta os parâmetros da requisição (ex: ?table_name=routines&user_id=3)
    table_name = request.args.get('table_name')
    filters = {key: value for key, value in request.args.items() if key != 'table_name'}

    # Validação básica: table_name é obrigatório
    if not table_name:
        return jsonify({'error': 'Parâmetro "table_name" é obrigatório.'}), 400

    try:
        # Cria a cláusula WHERE com base nos filtros fornecidos
        where_clause = build_where_clause(filters)

        # Executa a query principal com a cláusula WHERE
        query = f"SELECT * FROM {table_name}{where_clause}"
        cursor.execute(query, tuple(filters.values()))
        table_data = cursor.fetchall()

        # Guarda os nomes das colunas da tabela principal
        main_columns = [desc[0] for desc in cursor.description]

        # Retorno caso não haja dados
        if not table_data:
            return jsonify({'error': f'Nenhum dado encontrado para a tabela {table_name}'}), 404

        # Query para descobrir as chaves estrangeiras da tabela
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

        # Estrutura para armazenar os dados das tabelas estrangeiras
        foreign_data = {}

        # Para cada chave estrangeira, busca os dados correspondentes
        for fk in foreign_keys:
            column_name = fk[0]
            foreign_table_name = fk[1]
            foreign_column_name = fk[2]

            # Busca todos os dados das tabelas relacionadas
            join_query = f"""
                SELECT {foreign_table_name}.* 
                FROM {foreign_table_name}
                WHERE {foreign_table_name}.{foreign_column_name} IN (
                    SELECT {table_name}.{column_name} FROM {table_name}
                )
            """
            cursor.execute(join_query)
            foreign_values = cursor.fetchall()

            # Se a tabela relacionada tiver dados, salva no dicionário
            if foreign_values:
                column_names = [desc[0] for desc in cursor.description]
                foreign_data[column_name] = {
                    "foreign_table_name": foreign_table_name,
                    "columns": column_names,
                    "values": foreign_values
                }
            else:
                foreign_data[column_name] = {"error": "No foreign data found"}

        # Monta a resposta principal com os dados da tabela
        response = {
            'table': table_name,
            'data': [],
            'foreign_values': foreign_data
        }

        # Constrói lista de dicionários com os dados da tabela principal
        for row in table_data:
            row_data = {}
            for idx, col_name in enumerate(main_columns):
                if idx < len(row):
                    row_data[col_name] = row[idx]
            response['data'].append(row_data)

        # Retorna a resposta final como JSON
        return jsonify(response)

    except Exception as e:
        # Retorna erro genérico se algo falhar durante o processo
        return jsonify({'error': str(e)}), 500

    finally:
        # Fecha cursor e conexão com o banco
        cursor.close()
        conn.close()

# Configuração da execução do servidor Flask
if __name__ == '__main__':
    app.config['ENV'] = 'production'  # Define ambiente de execução
    app.run(host='0.0.0.0', port=5003, threaded=True)  # Executa em todas as interfaces na porta 5003
