# Importy bibliotek
import pygame, sys, pygame_gui
import random
import time
import os

# Importy z plikow projektu
from src.core.config import *
from src.core.ui import Button
from src.core.entities import Tile
from src.network.http_client import api_client
from src.network.ws_client import ws_client
from src.network.mqtt_client import mqtt_client

# --- GLOWNA KLASA GRY ONLINE ---
class OnlineGameManager:
    def __init__(self, screen):
        """Inicjalizacja menadzera gry online i ladowanie zasobow"""
        self.SCREEN = screen
        self.clock = pygame.time.Clock()
        self.MANAGER = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.load_assets()
        
        self.notification_text = ""
        self.notification_timer = 0
        
        # MQTT variables
        self.alert_message = None
        self.alert_box_ui = None
        self.alert_close_rect = None
        
        # Zmienna do kontroli generowania kafelkow
        self.last_generated_tile = None
        
        # Dźwięki
        self.CLICK = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "old-radio-button-click.mp3"))
        self.END = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "vinyl-stop-sound-effect.mp3"))
        self.CLICK2 = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "shamisen.mp3"))

    def load_assets(self):
        """Ladowanie grafik tła, przyciskow i kafelkow"""
        def get_img(name): return pygame.image.load(os.path.join(ASSETS_DIR, name))
        def get_bg_img(name): 
             img = pygame.image.load(os.path.join(ASSETS_DIR, name))
             return pygame.transform.scale(img, (500, 800))
             
        self.button_image = get_img("blue_button.png")
        self.black_button_image = get_img("black_button.png")
        self.red_button_image = get_img("red_button.png")
        self.yellow_button_image = get_img("yellow_button.png")
        self.green_button_image = get_img("green_button.png")
        
        self.background = get_img("background.png")
        
        self.easy_bg = get_bg_img("easy_game_background.jpg")
        self.normal_bg = get_bg_img("normal_game_background.jpg")
        self.hard_bg = get_bg_img("hard_game_background.jpg")
        self.boss_bg = get_bg_img("boss_game_background.jpg")
        
        self.easy_tile = os.path.join(ASSETS_DIR, "green_kanji.png")
        self.normal_tile = os.path.join(ASSETS_DIR, "yellow_kanji.png")
        self.hard_tile = os.path.join(ASSETS_DIR, "red_kanji.png")
        self.boss_tile = os.path.join(ASSETS_DIR, "white_kanji.png")

    # --- FUNKCJE POMOCNICZE (UI) ---
    def get_font(self, size):
        return pygame.font.Font(os.path.join(ASSETS_DIR, "The Last Shuriken.ttf"), size)

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.SCREEN.blit(img, (x, y))

    def play_music(self, track_name):
        """Odtwarzanie muzyki w tle"""
        pygame.mixer.music.load(os.path.join(ASSETS_DIR, track_name))
        if not pygame.mixer.music.get_busy(): pygame.mixer.music.play(-1)

    # --- POWIADOMIENIA WEBSOCKET ---
    def check_notifications(self):
        """Sprawdza czy przyszla wiadomosc z Websocketa"""
        msg = ws_client.get_latest_message()
        if msg:
            self.notification_text = msg
            self.notification_timer = 180

    def draw_notification(self):
        """Rysuje powiadomienie (Toast) na górze ekranu"""
        if self.notification_timer > 0:
            pygame.draw.rect(self.SCREEN, BLACK, (10, 10, WIDTH-20, 60))
            pygame.draw.rect(self.SCREEN, GREEN, (10, 10, WIDTH-20, 60), 2)
            
            font = self.get_font(15)
            text_surf = font.render(self.notification_text, True, WHITE)
            text_rect = text_surf.get_rect(center=(WIDTH//2, 40))
            self.SCREEN.blit(text_surf, text_rect)
            
            self.notification_timer -= 1

    # --- POWIADOMIENIA MQTT (DUZY ALERT) ---
    def check_mqtt_alerts(self):
        """Sprawdza czy przyszla wiadomosc od Admina"""
        msg = mqtt_client.get_latest_message()
        if msg:
            self.show_alert_popup(msg)

    def show_alert_popup(self, text):
        """Tworzy okno z wiadomoscia"""
        self.alert_message = text
        
        # Marginesy
        MARGIN = 40
        w = WIDTH - 2 * MARGIN
        h = HEIGHT - 2 * MARGIN
        
        if self.alert_box_ui: self.alert_box_ui.kill()
        
        formatted_text = f"<font face='The Last Shuriken' color='#FFFFFF' size='5'>{text}</font>"
        
        self.alert_box_ui = pygame_gui.elements.UITextBox(
            html_text=formatted_text,
            relative_rect=pygame.Rect((MARGIN, MARGIN), (w, h)),
            manager=self.MANAGER
        )
        
        btn_size = 40
        self.alert_close_rect = pygame.Rect(WIDTH - MARGIN - btn_size, MARGIN, btn_size, btn_size)

    def draw_alert_background(self):
        """Rysuje czarne tlo pod alertem"""
        if self.alert_box_ui and self.alert_message:
            rect = self.alert_box_ui.relative_rect
            pygame.draw.rect(self.SCREEN, BLACK, rect)
            pygame.draw.rect(self.SCREEN, RED, rect, 3)

    def draw_alert_close_button(self):
        """Rysuje przycisk X na wierzchu (Recznie, bez klasy Button)"""
        if self.alert_message and self.alert_close_rect:
            # Tlo pod przyciskiem X
            pygame.draw.rect(self.SCREEN, BLACK, self.alert_close_rect)
            pygame.draw.rect(self.SCREEN, RED, self.alert_close_rect, 2)
            
            # Kolor X zalezy od myszki
            mouse_pos = pygame.mouse.get_pos()
            col = WHITE if self.alert_close_rect.collidepoint(mouse_pos) else RED
            
            # Rysowanie X
            font = self.get_font(30)
            text_surf = font.render("X", True, col)
            text_rect = text_surf.get_rect(center=self.alert_close_rect.center)
            self.SCREEN.blit(text_surf, text_rect)

    def handle_alert_events(self, event):
        """Obsluga klikniecia w X"""
        if self.alert_message and event.type == pygame.MOUSEBUTTONDOWN:
            if self.alert_close_rect and self.alert_close_rect.collidepoint(event.pos):
                if self.alert_box_ui: self.alert_box_ui.kill()
                self.alert_box_ui = None
                self.alert_message = None
                self.alert_close_rect = None
                self.CLICK.play()

    # --- START APLIKACJI ---
    def start(self):
        """Punkt wejscia - uruchamia ekran logowania"""
        self.play_music("background_music.mp3")
        self.online_auth_menu()

    # --- GLOWNA PETLA ROZGRYWKI (ONLINE) ---
    def run_game_loop(self, mode):
        """Obsluguje mechanike gry: spadajace kafelki, kolizje, wynik"""
        player_name = api_client.username if api_client.username else "Unknown"

        # Konfiguracja trybu
        if mode == "easy": bg, tile_img, color, music, base_speed = self.easy_bg, self.easy_tile, GREEN, "easy_music.mp3", 5
        elif mode == "normal": bg, tile_img, color, music, base_speed = self.normal_bg, self.normal_tile, YELLOW, "normal_music.mp3", 7
        elif mode == "hard": bg, tile_img, color, music, base_speed = self.hard_bg, self.hard_tile, RED, "hard_music.mp3", 10
        else: bg, tile_img, color, music, base_speed = self.boss_bg, self.boss_tile, GREY, "boss_music.mp3", 14

        self.play_music(music)
        pygame.display.set_caption(f"Shamisen Tiles Online ({mode})")
        
        tile_group = pygame.sprite.Group()
        
        # Pierwszy kafelek - losujemy pas
        start_lane = random.randint(0, 3)
        first_tile = Tile(start_lane * TILE_WIDTH, -TILE_HEIGHT_BASE, self.SCREEN, tile_img)
        tile_group.add(first_tile)
        self.last_generated_tile = first_tile

        score, speed, i = 0, base_speed, 1
        running = True

        while running:
            pos = None
            self.SCREEN.blit(bg, (0, 0))
            
            UI_REFRESH = self.clock.tick(60)/1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return
                
                self.handle_alert_events(event)
                
                # Blokujemy klikanie w gre gdy jest alert
                if not self.alert_message:
                    if event.type == pygame.MOUSEBUTTONDOWN: pos = event.pos
                
                self.MANAGER.process_events(event)

            # Logika gry (tylko gdy nie ma alertu)
            if not self.alert_message:
                for tile in tile_group:
                    tile.update(speed, color)
                    # Sprawdzenie trafienia
                    if pos and tile.alive and tile.check_collision(pos):
                        tile.alive = False; score += 1
                    # Sprawdzenie przegranej
                    if tile.rect.bottom >= HEIGHT and tile.alive:
                        self.END.play()
                        self.show_final_score(score, player_name, mode)
                        return

                # Generowanie nowych kafelkow
                if self.last_generated_tile.rect.top + speed >= 0:
                    lane = random.randint(0, 3)
                    new_x = lane * TILE_WIDTH
                    
                    new_y = self.last_generated_tile.rect.top - TILE_HEIGHT_BASE - 50
                    
                    new_tile = Tile(new_x, new_y, self.SCREEN, tile_img)
                    tile_group.add(new_tile)
                    self.last_generated_tile = new_tile

                # Przyspieszanie gry co 100 punktow
                if score > i*100: speed += 1; i += 1
            
            # --- NOTYFIKACJE I ALERTY ---
            self.check_notifications()
            self.draw_notification()
            
            self.check_mqtt_alerts()
            self.draw_alert_background()
            
            self.MANAGER.update(UI_REFRESH)
            self.MANAGER.draw_ui(self.SCREEN)
            
            self.draw_alert_close_button() # Rysujemy X na koncu, zeby byl widoczny
            
            self.draw_text(f"SCORE: {score}", self.get_font(BIGGER_DISPLAY_FONT_SIZE), color, 5, 5)
            pygame.display.update()

    # --- MENU WYBORU POZIOMU DO GRY ---
    def game_modes_menu(self):
        """Menu wyboru trudnosci przed rozpoczeciem gry"""
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            TITLE = self.get_font(50).render("ONLINE MODES", True, CYAN)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 75)))

            btns = [
                Button(self.black_button_image, (250, 200), "BOSS", self.get_font(BUTTON_FONT_SIZE), BLACK, WHITE),
                Button(self.red_button_image, (250, 325), "HARD", self.get_font(BUTTON_FONT_SIZE), RED, WHITE),
                Button(self.yellow_button_image, (250, 450), "NORMAL", self.get_font(BUTTON_FONT_SIZE), YELLOW, WHITE),
                Button(self.green_button_image, (250, 575), "EASY", self.get_font(BUTTON_FONT_SIZE), GREEN, WHITE),
                Button(self.button_image, (250, 700), "BACK", self.get_font(BUTTON_FONT_SIZE), CYAN, WHITE)
            ]

            for b in btns: b.changeColor(MOUSE); b.update(self.SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.handle_alert_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN and not self.alert_message:
                    if btns[4].checkForInput(MOUSE): self.CLICK2.play(); return
                    modes = ["boss", "hard", "normal", "easy"]
                    for i, m in enumerate(modes):
                        if btns[i].checkForInput(MOUSE):
                            self.CLICK2.play()
                            self.run_game_loop(m)
            
            # --- OBSLUGA POWIADOMIEN ---
            self.check_notifications(); self.draw_notification()
            self.check_mqtt_alerts(); self.draw_alert_background()
            
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN)
            self.draw_alert_close_button()
            pygame.display.update()

    # --- MENU WYBORU POZIOMU DO RANKINGU ---
    def ranking_mode_selection(self, ranking_type):
        """Menu wyboru poziomu trudnosci, dla ktorego chcemy zobaczyc ranking"""
        title_txt = "GLOBAL RANKS" if ranking_type == "global" else "MY RANKS"
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            TITLE = self.get_font(50).render(title_txt, True, CYAN)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 75)))

            btns = [
                Button(self.black_button_image, (250, 200), "BOSS", self.get_font(BUTTON_FONT_SIZE), BLACK, WHITE),
                Button(self.red_button_image, (250, 325), "HARD", self.get_font(BUTTON_FONT_SIZE), RED, WHITE),
                Button(self.yellow_button_image, (250, 450), "NORMAL", self.get_font(BUTTON_FONT_SIZE), YELLOW, WHITE),
                Button(self.green_button_image, (250, 575), "EASY", self.get_font(BUTTON_FONT_SIZE), GREEN, WHITE),
                Button(self.button_image, (250, 700), "BACK", self.get_font(BUTTON_FONT_SIZE), CYAN, WHITE)
            ]

            for b in btns: b.changeColor(MOUSE); b.update(self.SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.handle_alert_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN and not self.alert_message:
                    if btns[4].checkForInput(MOUSE): self.CLICK2.play(); return
                    
                    modes = ["boss", "hard", "normal", "easy"]
                    for i, m in enumerate(modes):
                        if btns[i].checkForInput(MOUSE): 
                            self.CLICK2.play()
                            self.show_ranking_list(m, ranking_type) 
            
            self.check_notifications(); self.draw_notification()
            self.check_mqtt_alerts(); self.draw_alert_background()
            
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN)
            self.draw_alert_close_button()
            pygame.display.update()

    # --- WYSWIETLANIE LISTY RANKINGOWEJ ---
    def show_ranking_list(self, mode, ranking_type):
        """Pobiera i wyswietla liste wynikow z API"""
        header_text = f"{ranking_type.upper()} - {mode.upper()}"
        
        data = api_client.get_ranking(mode, ranking_type)
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(30).render(header_text, True, CYAN)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 50)))
            
            if not data:
                INFO = self.get_font(20).render("Brak wynikow / Blad API", True, WHITE)
                self.SCREEN.blit(INFO, INFO.get_rect(center=(250, 300)))
            else:
                y = 120
                for idx, entry in enumerate(data, start=1):
                    name = entry.get('player_name', 'Unknown')
                    sc = entry.get('score', 0)
                    row_text = f"{idx}. {name}: {sc}"
                    
                    surf = self.get_font(20).render(row_text, True, WHITE)
                    self.SCREEN.blit(surf, surf.get_rect(center=(250, y)))
                    y += 35
            
            BACK = Button(self.button_image, (250, 700), "BACK", self.get_font(30), CYAN, WHITE)
            BACK.changeColor(MOUSE); BACK.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.handle_alert_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN and not self.alert_message:
                    if BACK.checkForInput(MOUSE): self.CLICK2.play(); return
            
            self.check_notifications(); self.draw_notification()
            self.check_mqtt_alerts(); self.draw_alert_background()
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN)
            self.draw_alert_close_button()
            pygame.display.update()

    # --- USTAWIENIA PROFILU ---
    def profile_settings_menu(self):
        """Menu glowne ustawien profilu: wyswietla dane i opcje"""
        profile_data = api_client.get_profile_data()
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(40).render("PROFILE SETTINGS", True, CYAN)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 75)))
            
            if profile_data:
                # Wyswietlanie danych
                self.draw_text(f"User: {profile_data.get('username')}", self.get_font(20), WHITE, 50, 150)
                self.draw_text(f"Role: {profile_data.get('role')}", self.get_font(20), WHITE, 50, 190)
                self.draw_text(f"Joined: {profile_data.get('created_at')}", self.get_font(20), WHITE, 50, 230)
            else:
                self.draw_text("Error fetching profile data", self.get_font(20), RED, 50, 150)

            # Przyciski
            CHANGE_PASS = Button(self.button_image, (250, 350), "CHANGE PASS", self.get_font(30), YELLOW, WHITE)
            DELETE_ACC = Button(self.button_image, (250, 470), "DELETE ACC", self.get_font(30), RED, WHITE)
            BACK = Button(self.button_image, (250, 650), "BACK", self.get_font(30), CYAN, WHITE)
            
            for b in [CHANGE_PASS, DELETE_ACC, BACK]: b.changeColor(MOUSE); b.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.handle_alert_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN and not self.alert_message:
                    if BACK.checkForInput(MOUSE): self.CLICK2.play(); return
                    
                    if CHANGE_PASS.checkForInput(MOUSE):
                        self.CLICK2.play()
                        self.change_password_menu()
                        
                    if DELETE_ACC.checkForInput(MOUSE):
                        self.CLICK2.play()
                        if self.delete_account_menu(): 
                            return True 

            self.check_notifications(); self.draw_notification()
            self.check_mqtt_alerts(); self.draw_alert_background()
            
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN)
            self.draw_alert_close_button()
            pygame.display.update()

    def change_password_menu(self):
        """Pod-menu do zmiany hasla"""
        pygame.display.set_caption("Shamisen Tiles (Change Password)")
        old_pass_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((150, 200), (200, 50)), manager=self.MANAGER)
        old_pass_entry.set_text_hidden(True)
        new_pass_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((150, 300), (200, 50)), manager=self.MANAGER)
        new_pass_entry.set_text_hidden(True)
        
        status_msg = ""; status_color = WHITE
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(30).render("CHANGE PASSWORD", True, YELLOW)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 100)))
            self.draw_text("Old Password:", self.get_font(20), WHITE, 150, 170)
            self.draw_text("New Password:", self.get_font(20), WHITE, 150, 270)
            if status_msg: self.draw_text(status_msg, self.get_font(20), status_color, 50, 360)
            
            CONFIRM = Button(self.green_button_image, (250, 450), "CONFIRM", self.get_font(30), GREEN, WHITE)
            BACK = Button(self.button_image, (250, 600), "BACK", self.get_font(30), CYAN, WHITE)
            
            for b in [CONFIRM, BACK]: b.changeColor(MOUSE); b.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.handle_alert_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN and not self.alert_message:
                    if BACK.checkForInput(MOUSE): 
                        self.CLICK2.play(); old_pass_entry.kill(); new_pass_entry.kill(); return
                    
                    if CONFIRM.checkForInput(MOUSE):
                        self.CLICK2.play()
                        old = old_pass_entry.get_text()
                        new = new_pass_entry.get_text()
                        if len(new) < 4:
                            status_msg = "New password too short!"; status_color = RED
                        else:
                            success, msg = api_client.change_password(old, new)
                            status_msg = msg; status_color = GREEN if success else RED
                            if success: 
                                old_pass_entry.set_text(""); new_pass_entry.set_text("")

                self.MANAGER.process_events(event)
            
            self.check_notifications(); self.draw_notification()
            self.check_mqtt_alerts(); self.draw_alert_background()
            
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN)
            self.draw_alert_close_button()
            pygame.display.update()

    def delete_account_menu(self):
        """Pod-menu usuwania konta (wymaga hasla)"""
        pygame.display.set_caption("Shamisen Tiles (Delete Account)")
        pass_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((150, 300), (200, 50)), manager=self.MANAGER)
        pass_entry.set_text_hidden(True)
        status_msg = ""; status_color = WHITE
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(30).render("DELETE ACCOUNT", True, RED)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 100)))
            
            WARN1 = self.get_font(20).render("ARE YOU SURE?", True, WHITE)
            WARN2 = self.get_font(15).render("This cannot be undone!", True, RED)
            self.SCREEN.blit(WARN1, WARN1.get_rect(center=(250, 180)))
            self.SCREEN.blit(WARN2, WARN2.get_rect(center=(250, 210)))
            
            self.draw_text("Confirm Password:", self.get_font(20), WHITE, 150, 270)
            if status_msg: self.draw_text(status_msg, self.get_font(20), status_color, 50, 370)
            
            DELETE = Button(self.red_button_image, (250, 480), "DELETE PERMANENTLY", self.get_font(20), RED, WHITE)
            BACK = Button(self.button_image, (250, 600), "CANCEL", self.get_font(30), CYAN, WHITE)
            
            for b in [DELETE, BACK]: b.changeColor(MOUSE); b.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.handle_alert_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN and not self.alert_message:
                    if BACK.checkForInput(MOUSE): 
                        self.CLICK2.play(); pass_entry.kill(); return False
                    
                    if DELETE.checkForInput(MOUSE):
                        self.CLICK2.play()
                        pwd = pass_entry.get_text()
                        success, msg = api_client.delete_account(pwd)
                        status_msg = msg; status_color = GREEN if success else RED
                        if success:
                            time.sleep(1.5)
                            pass_entry.kill()
                            return True 

                self.MANAGER.process_events(event)
            
            self.check_notifications(); self.draw_notification()
            self.check_mqtt_alerts(); self.draw_alert_background()
            
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN)
            self.draw_alert_close_button()
            pygame.display.update()

    # --- EKRAN KOŃCOWY ONLINE ---
    def show_final_score(self, score, name, mode):
        """Wyswietla wynik po przegranej, wysyla go i pokazuje TOP 5"""
        self.play_music("background_music.mp3")
        api_client.send_score(score, mode)
        print(f"[ONLINE] Wyslano wynik: {score} ({mode})")
        ranking_data = api_client.get_ranking(mode, "global")
        
        col = BLACK
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            
            SCORE_TEXT = self.get_font(30).render(f"SCORE: {score}", True, col)
            self.SCREEN.blit(SCORE_TEXT, SCORE_TEXT.get_rect(center=(250, 60)))
            RANK_LABEL = self.get_font(20).render("TOP 5 GLOBAL:", True, col)
            self.SCREEN.blit(RANK_LABEL, RANK_LABEL.get_rect(center=(250, 110)))
            
            y = 150
            if not ranking_data:
                INFO = self.get_font(20).render("No data...", True, col)
                self.SCREEN.blit(INFO, INFO.get_rect(center=(250, y)))
            else:
                for idx, entry in enumerate(ranking_data[:5], start=1):
                    p_name = entry.get('player_name', 'Unknown')
                    p_score = entry.get('score', 0)
                    row_text = f"{idx}. {p_name}: {p_score}"
                    text_col = RED if (p_name == name and p_score == score) else col
                    surf = self.get_font(20).render(row_text, True, text_col)
                    self.SCREEN.blit(surf, surf.get_rect(center=(250, y)))
                    y += 35

            AGAIN = Button(self.black_button_image, (250, 630), "AGAIN", self.get_font(45), col, WHITE)
            MENU = Button(self.black_button_image, (250, 740), "MENU", self.get_font(45), col, WHITE)
            for b in [AGAIN, MENU]: b.changeColor(MOUSE); b.update(self.SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.handle_alert_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN and not self.alert_message:
                    if AGAIN.checkForInput(MOUSE): self.CLICK2.play(); self.run_game_loop(mode); return
                    if MENU.checkForInput(MOUSE): self.CLICK2.play(); return
                self.MANAGER.process_events(event)
            
            self.check_notifications(); self.draw_notification()
            self.check_mqtt_alerts(); self.draw_alert_background()
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN)
            self.draw_alert_close_button()
            pygame.display.update()

    # --- LOGOWANIE I REJESTRACJA ---
    def online_auth_menu(self):
        """Obsluguje formularz logowania i rejestracji"""
        pygame.display.set_caption("Shamisen Tiles (Online Login)")
        user_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((150, 250), (200, 50)), manager=self.MANAGER)
        pass_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((150, 350), (200, 50)), manager=self.MANAGER)
        pass_entry.set_text_hidden(True)
        status_msg = ""; status_color = WHITE
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(40).render("LOGIN / REGISTER", True, CYAN)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 100)))
            self.SCREEN.blit(self.get_font(20).render("Username:", True, WHITE), (150, 220))
            self.SCREEN.blit(self.get_font(20).render("Password:", True, WHITE), (150, 320))
            if status_msg: self.SCREEN.blit(self.get_font(20).render(status_msg, True, status_color), (150, 410))

            LOGIN_BTN = Button(self.green_button_image, (250, 500), "LOGIN", self.get_font(30), GREEN, WHITE)
            REG_BTN = Button(self.yellow_button_image, (250, 610), "REGISTER", self.get_font(30), YELLOW, WHITE)
            BACK_BTN = Button(self.button_image, (250, 720), "BACK", self.get_font(30), CYAN, WHITE)
            
            for b in [LOGIN_BTN, REG_BTN, BACK_BTN]: b.changeColor(MOUSE); b.update(self.SCREEN)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                self.handle_alert_events(event)
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.alert_message:
                    if BACK_BTN.checkForInput(MOUSE): 
                        self.CLICK2.play(); user_entry.kill(); pass_entry.kill(); return
                    
                    if LOGIN_BTN.checkForInput(MOUSE):
                        self.CLICK2.play(); status_msg = "Logging in..."; pygame.display.update()
                        success, msg = api_client.login(user_entry.get_text(), pass_entry.get_text())
                        status_msg = msg; status_color = GREEN if success else RED
                        
                        if success: 
                            time.sleep(0.5)
                            user_entry.kill()
                            pass_entry.kill()
                            
                            # STARTUJEMY OBA KLIENTY: WS i MQTT
                            ws_client.start()
                            mqtt_client.start() 
                            
                            self.online_dashboard()
                            
                            # ZATRZYMUJEMY OBA PO WYLOGOWANIU
                            ws_client.stop()
                            mqtt_client.stop()
                            api_client.token = None
                            
                            # --- POWROT Z GRY (Po wylogowaniu/usunieciu konta) ---
                            # Odtwarzamy pola formularza
                            user_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((150, 250), (200, 50)), manager=self.MANAGER)
                            pass_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((150, 350), (200, 50)), manager=self.MANAGER)
                            pass_entry.set_text_hidden(True)
                            status_msg = "Logged out"
                            status_color = WHITE
                            
                    if REG_BTN.checkForInput(MOUSE):
                        self.CLICK2.play()
                        if len(pass_entry.get_text()) < 4: status_msg = "Password too short!"; status_color = RED
                        else:
                            success, msg = api_client.register(user_entry.get_text(), pass_entry.get_text())
                            status_msg = msg; status_color = GREEN if success else RED

                self.MANAGER.process_events(event)
            
            # --- OBSLUGA POWIADOMIEN WS I MQTT ---
            self.check_notifications(); self.draw_notification()
            self.check_mqtt_alerts(); self.draw_alert_background()
            
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN)
            self.draw_alert_close_button()
            pygame.display.update()

    # --- DASHBOARD (ONLINE ZONE) ---
    def online_dashboard(self):
        """Glowne menu po zalogowaniu - dostep do gry i rankingow"""
        pygame.display.set_caption(f"Shamisen Tiles (Online: {api_client.username})")
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            TITLE = self.get_font(40).render("ONLINE ZONE", True, CYAN)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 80)))
            USER_TEXT = self.get_font(20).render(f"User: {api_client.username}", True, GREEN)
            self.SCREEN.blit(USER_TEXT, USER_TEXT.get_rect(center=(250, 130)))
            
            # Definicja przyciskow menu
            PLAY = Button(self.button_image, (250, 220), "PLAY ONLINE", self.get_font(30), CYAN, WHITE)
            GLOBAL = Button(self.button_image, (250, 320), "GLOBAL RANK", self.get_font(30), CYAN, WHITE)
            PERSONAL = Button(self.button_image, (250, 420), "PERSONAL RANK", self.get_font(30), CYAN, WHITE)
            PROFILE = Button(self.button_image, (250, 520), "PROFILE", self.get_font(30), CYAN, WHITE)
            LOGOUT = Button(self.red_button_image, (250, 650), "LOGOUT", self.get_font(30), RED, WHITE)
            
            btns = [PLAY, GLOBAL, PERSONAL, PROFILE, LOGOUT]
            for b in btns: b.changeColor(MOUSE); b.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.handle_alert_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN and not self.alert_message:
                    if PLAY.checkForInput(MOUSE): self.CLICK2.play(); self.game_modes_menu() 
                    if GLOBAL.checkForInput(MOUSE): self.CLICK2.play(); self.ranking_mode_selection("global")
                    if PERSONAL.checkForInput(MOUSE): self.CLICK2.play(); self.ranking_mode_selection("personal")
                    
                    if PROFILE.checkForInput(MOUSE): 
                        self.CLICK2.play()
                        if self.profile_settings_menu(): return 
                    
                    if LOGOUT.checkForInput(MOUSE): 
                        self.CLICK2.play()
                        return

            self.check_notifications(); self.draw_notification()
            self.check_mqtt_alerts(); self.draw_alert_background()
            
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN)
            self.draw_alert_close_button()
            pygame.display.update()