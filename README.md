# Wykonal:
Kacper Korzekwa

## Name
Multiplayer_Shamisen_Tiles

## Description
- shamisen-tiles/
- │
- ├── assets/                 # folder z grafikami/muzyką
- │
- ├── server/                 # Backend (FastAPI + Baza Danych)
- │   ├── __init__.py         # (pusty)
- │   ├── app.py              # Główny plik serwera
- │   ├── database.py         # Konfiguracja bazy SQLite
- │   └── models.py           # Modele danych (User, Score, Logi)
- │
- ├── src/                    # Klient (Gra Pygame)
- │   ├── network/            # Logika komunikacji (Klient API)
- │   │   ├── __init__.py     # (pusty)
- │   │   ├── http_client.py  # Obsługa REST (logowanie, wyniki)
- │   │   ├── mqtt_client.py  # Obsługa MQTT (admin)
- │   │   └── ws_client.py    # Obsługa WebSocket (live ranking)
- │   │
- │   ├── __init__.py         # (pusty)
- │   ├── config.py           # Stałe, kolory i konfiguracja ścieżek
- │   ├── entities.py         # Klasa Tile (kafelki)
- │   ├── game.py             # Główna logika gry (Game Loop)
- │   └── ui.py               # Elementy interfejsu (Button)
- │
- ├── main.py                 # Plik startowy (launcher gry)
- ├── requirements.txt        # Lista bibliotek
- └── README.md               # Plik z opisem

## Plan realizacji projektu (Roadmap)
### Etap 1: Backend i Baza Danych (Setup)
- [ ] **Konfiguracja Bazy Danych**:
    - [ ] Uruchomienie SQLite z wykorzystaniem `SQLModel` (`server/database.py`).
    - [ ] Stworzenie modeli tabel: `User`, `Score` oraz `SystemLog` (do spełnienia wymogu różnorodności danych).
- [ ] **Autentykacja i Bezpieczeństwo**:
    - [ ] Implementacja hashowania haseł przy użyciu `bcrypt`.
    - [ ] Endpointy `/auth/register` oraz `/auth/login`.
    - [ ] Generowanie i weryfikacja tokenów JWT (`server/auth.py`).

### Etap 2: REST API
Implementacja operacji CRUD dla 4 typów zasobów:
- [ ] **Użytkownicy (`/users`)**: Pobieranie profilu, edycja danych, usuwanie konta.
- [ ] **Wyniki (`/scores`)**:
    - [ ] Wysyłanie nowego wyniku (POST).
    - [ ] Pobieranie rankingu (GET) z filtrowaniem (np. `?limit=10`).
    - [ ] Usuwanie wyników (DELETE).
- [ ] **Konfiguracja Gry (`/config`)**: Endpointy do pobierania ustawień trudności z serwera.
- [ ] **Logi Systemowe (`/logs`)**: Podgląd zdarzeń serwera (kto się zalogował, błędy itp.).
- [ ] **Wyszukiwanie**: Dodanie opcji szukania gracza po fragmencie nazwy (SQL `LIKE`).

### Etap 3: Integracja Klienta (Pygame)
- [ ] **Moduł Sieciowy (`src/network/`)**:
    - [ ] Stworzenie klienta HTTP (`requests`) do komunikacji z API.
    - [ ] Obsługa logowania i przechowywania tokena JWT w pamięci gry.
- [ ] **UI/UX**:
    - [ ] Dodanie ekranu logowania/rejestracji przed menu głównym.
    - [ ] Podpięcie ekranów rankingu pod dane z API (zamiast plików `.txt`).

### Etap 4: Protokoły Real-time
- [ ] **WebSocket (Frontendowy protokół)**:
    - [ ] Serwer: Endpoint `/ws/rankings` wysyłający powiadomienia o nowych rekordach.
    - [ ] Klient: Live-update tablicy wyników bez odświeżania.
- [ ] **MQTT (Backendowy protokół)**:
    - [ ] Implementacja "Panelu Admina" (skrypt wysyłający komendy).
    - [ ] Klient: Odbieranie komend (np. `SPEED_BOOST`, `KICK_PLAYER`) i reagowanie w czasie rzeczywistym w grze.

### Etap 5: Finalizacja
- [ ] **Dodatkowe funkcjonalności**:
    - [ ] Logowanie zdarzeń do pliku po stronie serwera.
    - [ ] Obsługa błędów połączenia (try-except) w kliencie (żeby gra nie crashowała offline).
