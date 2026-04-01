import pygame, sys
from src.core.config import *
from src.core.ui import Button

from src.core.offline.game import OfflineGameManager
from src.core.online.game import OnlineGameManager
from src.core.admin_panel import AdminPanel

class Launcher:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Ładowanie tła i przycisków tylko dla launchera
        self.background = pygame.image.load(os.path.join(ASSETS_DIR, "background.png"))
        self.button_image = pygame.image.load(os.path.join(ASSETS_DIR, "blue_button.png"))
        self.music_path = os.path.join(ASSETS_DIR, "background_music.mp3")

    def get_font(self, size):
        return pygame.font.Font(os.path.join(ASSETS_DIR, "The Last Shuriken.ttf"), size)

    def play_music(self):
        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.play(-1)

    def main_menu(self):
        self.play_music()
        pygame.display.set_caption("Shamisen Tiles (Launcher)")
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(60).render("SELECT MODE", True, WHITE)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 100)))
            
            # Przyciski wyboru trybu
            ONLINE = Button(self.button_image, (250, 250), "ONLINE", self.get_font(BUTTON_FONT_SIZE), WHITE, CYAN)
            OFFLINE = Button(self.button_image, (250, 375), "OFFLINE", self.get_font(BUTTON_FONT_SIZE), WHITE, CYAN)
            ADMIN = Button(self.button_image, (250, 500), "ADMIN", self.get_font(BUTTON_FONT_SIZE), WHITE, RED)
            QUIT = Button(self.button_image, (250, 625), "QUIT", self.get_font(BUTTON_FONT_SIZE), WHITE, CYAN)
            
            for b in [ONLINE, OFFLINE, ADMIN, QUIT]:
                b.changeColor(MOUSE)
                b.update(self.SCREEN)
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    
                    if ONLINE.checkForInput(MOUSE):
                        online_game = OnlineGameManager(self.SCREEN)
                        online_game.start()
                        self.play_music()
                        
                    if OFFLINE.checkForInput(MOUSE):
                        offline_game = OfflineGameManager(self.SCREEN)
                        offline_game.main_menu()
                        self.play_music()
                    
                    if ADMIN.checkForInput(MOUSE):
                        admin = AdminPanel(self.SCREEN)
                        admin.run()
                        self.play_music()

                    if QUIT.checkForInput(MOUSE):
                        pygame.quit(); sys.exit()
            
            self.clock.tick(FPS)
            pygame.display.update()