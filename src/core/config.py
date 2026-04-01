import pygame
import os
import sys

# --- KONFIGURACJA EKRANU ---
WIDTH, HEIGHT = 500, 800
FPS = 60

# --- KOLORY ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
GREY = (100, 100, 100)

# --- CZCIONKI I ASSETY ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

BUTTON_FONT_SIZE = 40
DISPLAY_FONT_SIZE = 30
BIGGER_DISPLAY_FONT_SIZE = 50

# --- USTAWIENIA GRY ---
TILE_WIDTH = 125
TILE_HEIGHT_BASE = 150

# --- SIEC (HTTP / WS) ---
SERVER_IP = os.getenv("SHAMISEN_SERVER_IP", "127.0.0.1")
SERVER_URL = f"http://{SERVER_IP}:8000"

# --- PROTOKOL MQTT (NOWOSC - ETAP 4) ---
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "shamisen_tiles/alert/global"