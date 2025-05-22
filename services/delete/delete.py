# Importações necessárias
from flask import Flask, request, jsonify          # Flask para criar API RESTful
from flask_cors import CORS                        # CORS para liberar o acesso de diferentes domínios
import psycopg2                                     # Biblioteca para conectar ao PostgreSQL
from dotenv import load_dotenv                      # Para carregar variáveis do .env
import os                                           # Para acessar variáveis de ambiente

# Carrega variáveis de ambiente definidas em .env (como DB_HOST, DB_USER, etc)
load_dotenv()

# Instancia o app Flask
app = Flask(__name__)

# Configura o CORS: aqui está liberado para qualquer origem (ideal restringir em produção)

CORS(app, resources={r"/*": {"origins": "*"}})

# Função para estabelecer conexão com o banco de dados PostgreSQL
def get_db_connection():
    """
    Retorna uma conexão ativa com o banco de dados.
    SRP: esta função tem uma única responsabilidade – conectar ao banco.
    """
    connection = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return connection

# Função auxiliar para construir a cláusula WHERE com base nos filtros
def build_where_clause(filters):
    """
    Constrói dinamicamente uma cláusula WHERE a partir de um dicionário de filtros.
    OCP: pode ser estendida para suportar operadores como >, <, LIKE, etc.
    """
    where_clause = ""
    if filters:
        where_clause = " WHERE " + \
            " AND ".join([f"{key} = %s" for key in filters.keys()])
    return where_clause

# Rota para deletar dados de uma tabela com filtros
@app.route('/api/delete', methods=['DELETE'])
def delete_from_table():
    """
    Endpoint DELETE que remove registros de uma tabela, com base em filtros fornecidos via query string.

    Exemplo de uso:
    DELETE /api/delete?table_name=routines&id=3
    """

    # Estabelece conexão com o banco e cria cursor
    conn = get_db_connection()
    cursor = conn.cursor()

    # Lê o nome da tabela e os filtros (query params)
    table_name = request.args.get('table_name')
    filters = {key: value for key, value in request.args.items() if key != 'table_name'}

    # Validação: table_name é obrigatório
    if not table_name:
        return jsonify({'error': 'Parâmetro "table_name" é obrigatório.'}), 400

    # Validação: pelo menos um filtro é necessário
    if not filters:
        return jsonify({'error': 'É necessário fornecer ao menos uma condição na cláusula WHERE.'}), 400

    try:
        # Monta cláusula WHERE
        where_clause = build_where_clause(filters)

        # Monta e executa o DELETE
        query = f"DELETE FROM {table_name}{where_clause}"
        cursor.execute(query, tuple(filters.values()))
        conn.commit()  # Confirma a transação

        # Se nenhum registro foi afetado
        if cursor.rowcount == 0:
            return jsonify({'error': 'Nenhum dado foi deletado. Verifique os filtros.'}), 404

        # Resposta de sucesso
        return jsonify({'message': 'Registro(s) deletado(s) com sucesso.'})

    except Exception as e:
        # Captura erro e retorna mensagem de erro
        return jsonify({'error': str(e)}), 500

    finally:
        # Garante o fechamento da conexão com o banco
        cursor.close()
        conn.close()

# Inicia o servidor Flask se o arquivo for executado diretamente
if __name__ == '__main__':
    app.config['ENV'] = 'production'  # Define o ambiente para produção
    app.run(host='0.0.0.0', port=5004, threaded=True)  # Inicia a API na porta 5004
