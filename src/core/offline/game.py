import pygame, sys, pygame_gui
import random
import time
import os
from src.core.config import *
from src.core.ui import Button
from src.core.entities import Tile

class OfflineGameManager:
    def __init__(self, screen):
        self.SCREEN = screen 
        self.clock = pygame.time.Clock()
        self.MANAGER = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.load_assets()
        
        # Dźwięki
        self.CLICK = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "old-radio-button-click.mp3"))
        self.END = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "vinyl-stop-sound-effect.mp3"))
        self.CLICK2 = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "shamisen.mp3"))

    def load_assets(self):
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

    def get_font(self, size):
        return pygame.font.Font(os.path.join(ASSETS_DIR, "The Last Shuriken.ttf"), size)

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.SCREEN.blit(img, (x, y))

    def play_music(self, track_name):
        pygame.mixer.music.load(os.path.join(ASSETS_DIR, track_name))
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

    # --- PĘTLA GRY (OFFLINE) ---
    def run_game_loop(self, mode, player_name):
        if mode == "easy": bg, tile_img, color, music, base_speed = self.easy_bg, self.easy_tile, GREEN, "easy_music.mp3", 10
        elif mode == "normal": bg, tile_img, color, music, base_speed = self.normal_bg, self.normal_tile, YELLOW, "normal_music.mp3", 15
        elif mode == "hard": bg, tile_img, color, music, base_speed = self.hard_bg, self.hard_tile, RED, "hard_music.mp3", 20
        else: bg, tile_img, color, music, base_speed = self.boss_bg, self.boss_tile, GREY, "boss_music.mp3", 25

        self.play_music(music)
        pygame.display.set_caption(f"Shamisen Tiles ({mode})")
        tile_group = pygame.sprite.Group()
        tile_group.add(Tile(random.randint(0, 10)*30, -TILE_HEIGHT_BASE, self.SCREEN, tile_img))

        score, speed, i = 0, base_speed, 1
        running = True

        while running:
            pos = None
            self.SCREEN.blit(bg, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return
                if event.type == pygame.MOUSEBUTTONDOWN: pos = event.pos

            for tile in tile_group:
                tile.update(speed, color)
                if pos and tile.alive and tile.check_collision(pos):
                    tile.alive = False; score += 1
                if tile.rect.bottom >= HEIGHT and tile.alive:
                    self.END.play()
                    self.show_final_score(score, player_name, mode)
                    return

            if len(tile_group) > 0 and tile_group.sprites()[-1].rect.top + speed >= 0:
                tile_group.add(Tile(random.randint(0, 10)*30, tile_group.sprites()[-1].rect.top - TILE_HEIGHT_BASE - 20, self.SCREEN, tile_img))

            if score > i*100: speed += 1; i += 1
            self.clock.tick(FPS)
            self.draw_text(f"SCORE: {score}", self.get_font(BIGGER_DISPLAY_FONT_SIZE), color, 5, 5)
            pygame.display.update()

    # --- EKRAN WPISYWANIA IMIENIA (TYLKO OFFLINE) ---
    def start_screen(self, mode):
        # Konfiguracja kolorów i obrazków w zależności od trybu
        colors = {"easy": GREEN, "normal": YELLOW, "hard": RED, "boss": BLACK}
        imgs = {"easy": self.green_button_image, "normal": self.yellow_button_image, 
                "hard": self.red_button_image, "boss": self.black_button_image}
        
        used_color = colors.get(mode, CYAN)
        btn_img = imgs.get(mode, self.button_image)
        
        text_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((155, 300), (200, 50)), manager=self.MANAGER)
        player_name = "Anonymous"
        name_saved = False # Flaga informująca, czy wyświetlić napis "Players name saved"

        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE_POS = pygame.mouse.get_pos()
            
            prompt = self.get_font(40).render("Enter name:", True, used_color)
            self.SCREEN.blit(prompt, prompt.get_rect(center=(250, 260)))

            # Przyciski w kolorze trybu
            START = Button(btn_img, (250, 575), "START", self.get_font(60), used_color, WHITE)
            BACK = Button(btn_img, (250, 700), "BACK", self.get_font(60), used_color, WHITE)

            for b in [START, BACK]: b.changeColor(MOUSE_POS); b.update(self.SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK.checkForInput(MOUSE_POS): self.CLICK2.play(); text_entry.kill(); return
                    if START.checkForInput(MOUSE_POS): 
                        self.CLICK2.play(); text_entry.kill(); time.sleep(1)
                        self.run_game_loop(mode, player_name); return
                
                if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    player_name = event.text
                    name_saved = True # Imię zatwierdzone, włączamy napis
                
                self.MANAGER.process_events(event)
            
            # Wyświetlanie komunikatu o zapisaniu imienia
            if name_saved:
                self.draw_text("Players name saved", self.get_font(BIGGER_DISPLAY_FONT_SIZE), used_color, 70, 380)

            self.MANAGER.update(UI_REFRESH)
            self.MANAGER.draw_ui(self.SCREEN)
            pygame.display.update()

    # --- MENU WYBORU POZIOMU ---
    def game_modes_menu(self):
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            MOUSE_POS = pygame.mouse.get_pos()
            TITLE = self.get_font(50).render("OFFLINE MODES", True, CYAN)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 75)))

            btns = [
                Button(self.black_button_image, (250, 200), "BOSS", self.get_font(BUTTON_FONT_SIZE), BLACK, WHITE),
                Button(self.red_button_image, (250, 325), "HARD", self.get_font(BUTTON_FONT_SIZE), RED, WHITE),
                Button(self.yellow_button_image, (250, 450), "NORMAL", self.get_font(BUTTON_FONT_SIZE), YELLOW, WHITE),
                Button(self.green_button_image, (250, 575), "EASY", self.get_font(BUTTON_FONT_SIZE), GREEN, WHITE),
                Button(self.button_image, (250, 700), "BACK", self.get_font(BUTTON_FONT_SIZE), CYAN, WHITE)
            ]

            for btn in btns: btn.changeColor(MOUSE_POS); btn.update(self.SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btns[4].checkForInput(MOUSE_POS): self.CLICK2.play(); return
                    modes = ["boss", "hard", "normal", "easy"]
                    for i, m in enumerate(modes):
                        if btns[i].checkForInput(MOUSE_POS): self.CLICK2.play(); self.start_screen(m)
            self.clock.tick(FPS); pygame.display.update()

    # --- ZAPIS PLIKOWY ---
    def save_local_score(self, name, score, mode):
        path = os.path.join(BASE_DIR, "offline_rankings", f"{mode}_ranking.txt")
        rankings = []
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    if ":" in line:
                        parts = line.strip().split(". ", 1)[1].split(": ")
                        rankings.append((parts[0], int(parts[1])))
        rankings.append((name, score))
        rankings.sort(key=lambda x: (-x[1], x[0]))
        
        with open(path, "w") as f:
            for i, (n, s) in enumerate(rankings[:10], 1): f.write(f"{i}. {n}: {s}\n")

    def show_final_score(self, score, name, mode):
        self.play_music("background_music.mp3")
        self.save_local_score(name, score, mode)
        
        # Konfiguracja kolorów dla ekranu końcowego
        colors = {"easy": GREEN, "normal": YELLOW, "hard": RED, "boss": BLACK}
        imgs = {"easy": self.green_button_image, "normal": self.yellow_button_image, 
                "hard": self.red_button_image, "boss": self.black_button_image}
        
        col = colors.get(mode, BLACK)
        img = imgs.get(mode, self.black_button_image)
        
        path = os.path.join(BASE_DIR, "offline_rankings", f"{mode}_ranking.txt")
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            MOUSE = pygame.mouse.get_pos()
            self.draw_text(f"SCORE: {score}", self.get_font(30), col, 150, 60)
            self.draw_text("Offline Ranking:", self.get_font(20), col, 130, 150)
            
            y = 200
            if os.path.exists(path):
                with open(path, "r") as f:
                    for line in f:
                        self.draw_text(line.strip(), self.get_font(20), col, 50, y); y += 40

            AGAIN = Button(img, (250, 630), "AGAIN", self.get_font(45), col, WHITE)
            MENU = Button(img, (250, 740), "MENU", self.get_font(45), col, WHITE)
            for b in [AGAIN, MENU]: b.changeColor(MOUSE); b.update(self.SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if AGAIN.checkForInput(MOUSE): self.CLICK2.play(); self.start_screen(mode); return
                    if MENU.checkForInput(MOUSE): self.CLICK2.play(); return
            self.clock.tick(FPS); pygame.display.update()

    # --- RANKINGI ---
    def ranking_menu(self):
        pygame.display.set_caption("Shamisen Tiles (rankings)")
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            MOUSE = pygame.mouse.get_pos()
            
            MENU_TEXT = self.get_font(50).render("RANKINGS", True, CYAN)
            self.SCREEN.blit(MENU_TEXT, MENU_TEXT.get_rect(center=(250, 75)))

            btns = [
                Button(self.black_button_image, (250, 200), "BOSS", self.get_font(BUTTON_FONT_SIZE), BLACK, WHITE),
                Button(self.red_button_image, (250, 325), "HARD", self.get_font(BUTTON_FONT_SIZE), RED, WHITE),
                Button(self.yellow_button_image, (250, 450), "NORMAL", self.get_font(BUTTON_FONT_SIZE), YELLOW, WHITE),
                Button(self.green_button_image, (250, 575), "EASY", self.get_font(BUTTON_FONT_SIZE), GREEN, WHITE),
                Button(self.button_image, (250, 700), "BACK", self.get_font(BUTTON_FONT_SIZE), CYAN, WHITE)
            ]

            for btn in btns: btn.changeColor(MOUSE); btn.update(self.SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btns[4].checkForInput(MOUSE): self.CLICK2.play(); return
                    
                    modes = ["boss", "hard", "normal", "easy"]
                    for i, mode in enumerate(modes):
                        if btns[i].checkForInput(MOUSE):
                            self.CLICK2.play()
                            self.show_ranking_screen(mode)

            self.clock.tick(FPS); pygame.display.update()

    def show_ranking_screen(self, mode):
        # Konfiguracja kolorów dla ekranu rankingu
        colors = {"easy": GREEN, "normal": YELLOW, "hard": RED, "boss": BLACK}
        imgs = {"easy": self.green_button_image, "normal": self.yellow_button_image, 
                "hard": self.red_button_image, "boss": self.black_button_image}
        
        col = colors.get(mode, CYAN)
        btn_img = imgs.get(mode, self.button_image)
        
        path = os.path.join(BASE_DIR, "offline_rankings", f"{mode}_ranking.txt")

        while True:
            self.SCREEN.blit(self.background, (0, 0))
            MOUSE = pygame.mouse.get_pos()

            RANK_TEXT = self.get_font(BUTTON_FONT_SIZE).render("RANKING:", True, col)
            self.SCREEN.blit(RANK_TEXT, RANK_TEXT.get_rect(center=(250, 50)))
            
            y_value = 125
            if os.path.exists(path):
                with open(path, "r") as f:
                    for line in f:
                        score_text = self.get_font(DISPLAY_FONT_SIZE).render(line.strip(), True, col)
                        self.SCREEN.blit(score_text, score_text.get_rect(center=(250, y_value)))
                        y_value += 50

            BACK_BTN = Button(btn_img, (250, 700), "BACK", self.get_font(BUTTON_FONT_SIZE), col, WHITE)
            BACK_BTN.changeColor(MOUSE)
            BACK_BTN.update(self.SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BTN.checkForInput(MOUSE):
                        self.CLICK2.play()
                        return

            self.clock.tick(FPS); pygame.display.update()

    # --- MENU GŁÓWNE OFFLINE ---
    def main_menu(self):
        self.play_music("background_music.mp3")
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            MOUSE = pygame.mouse.get_pos()
            TITLE = self.get_font(80).render("OFFLINE", True, CYAN)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 100)))
            
            PLAY = Button(self.button_image, (250, 250), "PLAY", self.get_font(45), CYAN, WHITE)
            RANKING = Button(self.button_image, (250, 400), "RANKING", self.get_font(45), CYAN, WHITE)
            QUIT = Button(self.button_image, (250, 550), "QUIT", self.get_font(45), CYAN, WHITE)
            BACK = Button(self.button_image, (250, 700), "BACK", self.get_font(45), CYAN, WHITE)
            
            for b in [PLAY, RANKING, QUIT, BACK]: b.changeColor(MOUSE); b.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY.checkForInput(MOUSE): self.CLICK2.play(); self.game_modes_menu()
                    if RANKING.checkForInput(MOUSE): self.CLICK2.play(); self.ranking_menu()
                    if QUIT.checkForInput(MOUSE): pygame.quit(); sys.exit()
                    if BACK.checkForInput(MOUSE): self.CLICK2.play(); return 
            self.clock.tick(FPS); pygame.display.update()