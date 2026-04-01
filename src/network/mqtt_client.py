import paho.mqtt.client as mqtt
import queue
import threading
from src.core.config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.message_queue = queue.Queue()
        self.is_connected = False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[MQTT] Polaczono z brokerem!")
            self.is_connected = True
            client.subscribe(MQTT_TOPIC)
        else:
            print(f"[MQTT] Blad polaczenia, kod: {rc}")

    def on_message(self, client, userdata, msg):
        """Odbiera wiadomosc i wrzuca do kolejki"""
        try:
            payload = msg.payload.decode('utf-8')
            print(f"[MQTT] Odebrano wiadomosc: {payload}")
            self.message_queue.put(payload)
        except Exception as e:
            print(f"[MQTT] Blad dekodowania: {e}")

    def start(self):
        try:
            print(f"[MQTT] Laczenie z {MQTT_BROKER}...")
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTT] Nie mozna polaczyc: {e}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.is_connected = False

    def publish_message(self, text):
        """Wysyla wiadomosc globalna"""
        if self.is_connected:
            self.client.publish(MQTT_TOPIC, text)
            print(f"[MQTT] WYSŁANO: {text}")
            return True
        return False

    def get_latest_message(self):
        """Zwraca wiadomosc z kolejki"""
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None

mqtt_client = MQTTClient()