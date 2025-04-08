import json
import time
import psycopg2
from paho.mqtt import client as mqtt_client

# Configurações do PostgreSQL
db_config = {
    "host": "localhost",        # ou IP do servidor PostgreSQL
    "port": 5432,
    "dbname": "espacobuddy",
    "user": "postgres",
    "password": "postgres"
}

# Configurações MQTT (com broker público Mosquitto)
broker = 'test.mosquitto.org'
port = 1883
topic = "menu/params/get/espacobuddy"  # use um tópico exclusivo
client_id = f'cliente-mqtt-{int(time.time())}'

# Salvar dados no PostgreSQL
# Atualizar status na tabela Feeder
def update_feeder_status(feeder_id, status):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE feeder
            SET status = %s
            WHERE id = %s
        """, (status, feeder_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[BD] Feeder {feeder_id} atualizado com status = {status}")
    except Exception as e:
        print(f"[ERRO BD] Falha ao atualizar feeder: {e}")

# Callback MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Conectado a {broker}")
        client.subscribe(topic)
        print(f"[MQTT] Inscrito em '{topic}'")
    else:
        print(f"[MQTT] Erro ao conectar. Código: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        feeder_id = payload.get("id")
        status = payload.get("status")

        if feeder_id is not None and status is not None:
            atualizar_status_feeder(feeder_id, status)
        else:
            print(f"[ERRO] JSON incompleto: {payload}")
    except Exception as e:
        print(f"[ERRO] Falha ao processar mensagem: {e}")

# Main loop
def run():
    client = mqtt_client.Client(client_id=client_id, protocol=mqtt_client.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, port)
    client.loop_forever()

if __name__ == '__main__':
    run()
