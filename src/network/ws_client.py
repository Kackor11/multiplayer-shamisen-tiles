import asyncio
import websockets
import threading
import queue
from src.core.config import SERVER_URL

class WebSocketClient:
    def __init__(self):
        base = SERVER_URL.rstrip("/")
        self.ws_url = base.replace("http", "ws") + "/ws/rankings"
        
        self.message_queue = queue.Queue()
        self.running = False
        self.thread = None

    def start(self):
        """Uruchamia nasluchiwanie w osobnym watku"""
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()
        print(f"[WS] Start klienta na adres: {self.ws_url}")

    def stop(self):
        """Zatrzymuje nasluchiwanie"""
        self.running = False

    def _run_async_loop(self):
        """Pętla asyncio uruchamiana w watku"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._listen())

    async def _listen(self):
        """Laczy sie z serwerem i czeka na wiadomosci"""
        while self.running:
            try:
                async with websockets.connect(self.ws_url, ping_interval=None) as websocket:
                    print("[WS] Polaczono z serwerem!")
                    while self.running:
                        try:
                            message = await websocket.recv()
                            self.message_queue.put(message)
                            print(f"[WS] Otrzymano wiadomosc: {message}")
                        except websockets.ConnectionClosed:
                            print("[WS] Polaczenie zamkniete, ponawiam...")
                            break
            except Exception as e:
                await asyncio.sleep(3)

    def get_latest_message(self):
        """Zwraca najnowsza wiadomosc z kolejki (lub None)"""
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None

# Singleton
ws_client = WebSocketClient()