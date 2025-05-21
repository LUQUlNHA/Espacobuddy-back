import psycopg2
import os
import time as time_module
from datetime import datetime, timedelta, time
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import json
from Routine import Routine

load_dotenv()

executed_routines = []

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC_ROUTINE")

mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)  # ou MQTTv5 para o novo

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        print("Connected to MQTT Broker")

    mqtt_client.on_connect = on_connect
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_start()

def publish(routine, msg):
    final_topic = f"{MQTT_TOPIC}/{routine.feeder_id}"
    payload = json.dumps(msg)

    mqtt_client.publish(final_topic, payload)
    print(f"📡 Publicado no MQTT [{final_topic}]: {payload}")

def check_routine_schedule(routine):
    now = datetime.now()
    current_time = time(now.hour, now.minute)  # Hora atual (HH:MM)
    scheduled_time_clean = time(routine.schedule_time.hour, routine.schedule_time.minute)

    for entry in executed_routines:
        if entry['routine_id'] == routine.id:
            last_datetime = datetime.combine(now.date(), entry['executed_time'])
            if now - last_datetime < timedelta(hours=24):
                print(f"Rotina ja executada: [{routine.id} - {routine.routine_name}]")
                return  # Já executou nas últimas 24h
            break  # Pode executar se passou 24h

    if scheduled_time_clean == current_time:
        msg = {
            "routine": routine.to_dict(),
            "device_id": routine.feeder_id
        }

        publish(routine, msg)

        # Atualiza ou insere a rotina na lista
        for entry in executed_routines:
            if entry['routine_id'] == routine.id:
                entry['executed_time'] = routine.schedule_time
                break
        else:
            executed_routines.append({
                'routine_id': routine.id,
                'executed_time': routine.schedule_time
            })

def get_routines() -> list:
    conn = None
    routines = []
    try:
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

            for row in rows:
                routine = Routine(*row)
                routines.append(routine)

    except Exception as e:
        print(f"❌ Erro ao buscar rotinas: {e}")
    finally:
        if conn:
            conn.close()

    print(f"Lista tamanho: {len(routines)}")
    return routines

if __name__ == "__main__":
    connect_mqtt()
    print("Connecting to MQTT")

    try:
        while True:
            routines = get_routines()

            for routine in routines:
                check_routine_schedule(routine)

            time_module.sleep(1) 
    except Exception as error:
        print(f"Exit! Error Description: [{error}]")
        mqtt_client.loop_stop()
