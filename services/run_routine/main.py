# Importa bibliotecas necessárias
import psycopg2  # Conexão com PostgreSQL
import os  # Acesso a variáveis de ambiente
import time as time_module  # Usado para pausa entre ciclos
from datetime import datetime, timedelta, time  # Manipulação de tempo e datas
from dotenv import load_dotenv  # Carregamento de variáveis do arquivo .env
import paho.mqtt.client as mqtt  # Cliente MQTT
import json  # Serialização JSON
from Routine import Routine  # Importa a classe Routine

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Lista de rotinas já executadas, para evitar reexecução
executed_routines = []

# Recupera dados do broker MQTT a partir do .env
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC_ROUTINE")

# Instancia o cliente MQTT
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)  # Usa protocolo MQTT 3.1.1

# Função de conexão MQTT
def connect_mqtt():
    """
    Conecta o cliente MQTT ao broker.
    Define callback on_connect e inicia o loop do cliente.
    """
    def on_connect(client, userdata, flags, rc):
        print("Connected to MQTT Broker")

    mqtt_client.on_connect = on_connect
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_start()

# Publica uma mensagem no tópico do alimentador
def publish(routine, msg):
    """
    Publica uma mensagem JSON formatada para o tópico específico do alimentador.

    Parâmetros:
    - routine: Objeto Routine.
    - msg: Dicionário JSON com os dados da rotina.
    """
    final_topic = f"{MQTT_TOPIC}/{routine.feeder_id}"
    payload = json.dumps(msg)

    mqtt_client.publish(final_topic, payload)
    print(f"📡 Publicado no MQTT [{final_topic}]: {payload}")

# Verifica se uma rotina deve ser executada com base no horário
def check_routine_schedule(routine):
    """
    Verifica se a rotina está agendada para o horário atual e se já foi executada
    nas últimas 24 horas. Em caso positivo, publica a mensagem via MQTT.

    Parâmetros:
    - routine: Objeto Routine.
    """
    now = datetime.now()
    current_time = time(now.hour, now.minute)
    scheduled_time_clean = time(routine.schedule_time.hour, routine.schedule_time.minute)

    # Verifica se já foi executada recentemente
    for entry in executed_routines:
        if entry['routine_id'] == routine.id:
            last_datetime = datetime.combine(now.date(), entry['executed_time'])
            if now - last_datetime < timedelta(hours=24):
                print(f"Rotina ja executada: [{routine.id} - {routine.routine_name}]")
                return
            break  # Se passou mais de 24h, pode executar

    # Se o horário atual bate com o agendado, executa
    if scheduled_time_clean == current_time:
        msg = {
            "routine": routine.to_dict(),
            "device_id": routine.feeder_id
        }

        publish(routine, msg)

        # Atualiza a lista de rotinas executadas
        for entry in executed_routines:
            if entry['routine_id'] == routine.id:
                entry['executed_time'] = routine.schedule_time
                break
        else:
            executed_routines.append({
                'routine_id': routine.id,
                'executed_time': routine.schedule_time
            })

# Busca todas as rotinas salvas no banco de dados PostgreSQL
def get_routines() -> list:
    """
    Conecta ao banco de dados e retorna uma lista de objetos Routine.

    Retorna:
    - Lista de rotinas instanciadas a partir dos dados da tabela.
    """
    conn = None
    routines = []
    try:
        # Estabelece conexão com o banco
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        with conn.cursor() as cur:
            cur.execute("SELECT id, routine_name, feeder_id, schedule_time, portion_size, user_id FROM routines;")
            rows = cur.fetchall()

            # Constrói objetos Routine com os dados
            for row in rows:
                routine = Routine(*row)
                routines.append(routine)

    except Exception as e:
        print(f"❌ Erro ao buscar rotinas: {e}")
    finally:
        if conn:
            conn.close()  # Garante que a conexão será encerrada

    print(f"Lista tamanho: {len(routines)}")
    return routines

# Execução principal do serviço
if __name__ == "__main__":
    connect_mqtt()
    print("Connecting to MQTT")

    try:
        # Loop principal do serviço
        while True:
            routines = get_routines()  # Recarrega rotinas a cada segundo

            for routine in routines:
                check_routine_schedule(routine)  # Verifica e publica se necessário

            time_module.sleep(1)  # Pausa de 1 segundo para evitar sobrecarga

    except Exception as error:
        print(f"Exit! Error Description: [{error}]")
        mqtt_client.loop_stop()  # Encerra o loop MQTT com segurança
