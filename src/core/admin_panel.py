import pygame, pygame_gui
import sys
import os
from src.core.config import *
from src.core.ui import Button
from src.network.http_client import api_client
from src.network.mqtt_client import mqtt_client

class AdminPanel:
    def __init__(self, screen):
        self.SCREEN = screen
        self.clock = pygame.time.Clock()
        self.MANAGER = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.load_assets()
        
    def load_assets(self):
        self.background = pygame.image.load(os.path.join(ASSETS_DIR, "background.png"))
        self.button_image = pygame.image.load(os.path.join(ASSETS_DIR, "blue_button.png"))
        self.red_btn = pygame.image.load(os.path.join(ASSETS_DIR, "red_button.png"))
        
    def get_font(self, size):
        return pygame.font.Font(os.path.join(ASSETS_DIR, "The Last Shuriken.ttf"), size)

    def draw_text(self, text, font, col, x, y):
        self.SCREEN.blit(font.render(text, True, col), (x, y))

    # --- MENU GŁÓWNE ADMINA ---
    def run(self):
        if not self.admin_login_screen():
            return

        mqtt_client.start()
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(40).render("ADMIN PANEL", True, RED)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 80)))
            
            PLAYERS = Button(self.button_image, (250, 160), "PLAYERS LIST", self.get_font(30), WHITE, YELLOW)
            SEARCH = Button(self.button_image, (250, 260), "SEARCH PLAYER", self.get_font(30), WHITE, YELLOW)
            LOGS = Button(self.button_image, (250, 360), "SYSTEM LOGS", self.get_font(30), WHITE, YELLOW)
            MESSAGE = Button(self.red_btn, (250, 480), "SEND MESSAGE", self.get_font(30), WHITE, RED)
            LOGOUT = Button(self.button_image, (250, 650), "LOGOUT", self.get_font(30), WHITE, RED)
            
            for b in [PLAYERS, SEARCH, LOGS, MESSAGE, LOGOUT]:
                b.changeColor(MOUSE)
                b.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAYERS.checkForInput(MOUSE): self.players_list_screen()
                    if SEARCH.checkForInput(MOUSE): self.search_player_screen()
                    if LOGS.checkForInput(MOUSE): self.logs_screen()
                    if MESSAGE.checkForInput(MOUSE): self.send_message_screen()
                    
                    if LOGOUT.checkForInput(MOUSE): 
                        mqtt_client.stop()
                        api_client.token = None
                        return

            self.clock.tick(FPS)
            pygame.display.update()

    # --- EKRAN WYSYŁANIA WIADOMOŚCI (MQTT) ---
    def send_message_screen(self):
        msg_entry = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((50, 150), (400, 200)),
            manager=self.MANAGER
        )
        msg_entry.set_text("Hello Players!")
        status_msg = ""
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(35).render("GLOBAL MESSAGE", True, RED)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 80)))
            
            self.draw_text("Type your message below:", self.get_font(20), WHITE, 50, 120)
            if status_msg: self.draw_text(status_msg, self.get_font(20), GREEN, 50, 370)
            
            SEND = Button(self.red_btn, (250, 450), "SEND TO ALL", self.get_font(30), WHITE, RED)
            BACK = Button(self.button_image, (250, 650), "BACK", self.get_font(30), WHITE, CYAN)
            
            for b in [SEND, BACK]: b.changeColor(MOUSE); b.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK.checkForInput(MOUSE): 
                        msg_entry.kill(); return
                    
                    if SEND.checkForInput(MOUSE):
                        text = msg_entry.get_text()
                        if text:
                            mqtt_client.publish_message(text)
                            status_msg = "Message Sent!"
                            msg_entry.set_text("")
                        else:
                            status_msg = "Cannot send empty!"

                self.MANAGER.process_events(event)
            
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN); pygame.display.update()

    # --- EKRAN LOGOWANIA ADMINA ---
    def admin_login_screen(self):
        user_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((150, 250), (200, 50)), manager=self.MANAGER)
        pass_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((150, 350), (200, 50)), manager=self.MANAGER)
        pass_entry.set_text_hidden(True)
        status_msg = ""
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(40).render("ADMIN LOGIN", True, RED)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 100)))
            self.draw_text("Username:", self.get_font(20), WHITE, 150, 220)
            self.draw_text("Password:", self.get_font(20), WHITE, 150, 320)
            if status_msg: self.draw_text(status_msg, self.get_font(20), RED, 100, 420)
            
            LOGIN = Button(self.button_image, (250, 500), "LOGIN", self.get_font(30), WHITE, GREEN)
            BACK = Button(self.button_image, (250, 650), "BACK", self.get_font(30), WHITE, CYAN)
            
            for b in [LOGIN, BACK]: b.changeColor(MOUSE); b.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK.checkForInput(MOUSE): 
                        user_entry.kill(); pass_entry.kill(); return False
                    
                    if LOGIN.checkForInput(MOUSE):
                        status_msg = "Checking..."
                        pygame.display.update()
                        success, msg = api_client.login(user_entry.get_text(), pass_entry.get_text())
                        if success:
                            profile = api_client.get_profile_data()
                            if profile and profile.get("role") == "admin":
                                user_entry.kill(); pass_entry.kill()
                                return True
                            else:
                                status_msg = "Not an Admin!"
                                api_client.token = None
                        else:
                            status_msg = msg

                self.MANAGER.process_events(event)
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN); pygame.display.update()

    # --- LISTA GRACZY ---
    def players_list_screen(self):
        users = api_client.admin_get_users()
        list_items = []
        if users:
            for u in users:
                short_pass = u['password_hash'][:10] + "..."
                created = u['created_at'][:10]
                list_items.append(f"{u['username']} | {short_pass} | {created}")
        else:
            list_items = ["No users found"]

        selection_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect((50, 150), (400, 400)),
            item_list=list_items,
            manager=self.MANAGER
        )

        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(30).render("PLAYERS LIST", True, YELLOW)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 80)))
            self.draw_text("Name | Hash | Date", self.get_font(20), WHITE, 50, 120)
            
            BACK = Button(self.button_image, (250, 650), "BACK", self.get_font(30), WHITE, CYAN)
            BACK.changeColor(MOUSE); BACK.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK.checkForInput(MOUSE): 
                        selection_list.kill(); return
                
                self.MANAGER.process_events(event)
            
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN); pygame.display.update()

    # --- WYSZUKIWANIE I EDYCJA ---
    def search_player_screen(self):
        search_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((100, 150), (300, 50)), manager=self.MANAGER)
        
        result_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect((50, 220), (400, 300)),
            item_list=[],
            manager=self.MANAGER
        )
        
        all_users = api_client.admin_get_users()
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(30).render("SEARCH PLAYER", True, YELLOW)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 80)))
            self.draw_text("Enter nickname:", self.get_font(20), WHITE, 100, 120)
            
            BACK = Button(self.button_image, (250, 650), "BACK", self.get_font(30), WHITE, CYAN)
            BACK.changeColor(MOUSE); BACK.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK.checkForInput(MOUSE): 
                        search_entry.kill(); result_list.kill(); return
                
                if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED and event.ui_element == search_entry:
                    query = event.text.lower()
                    filtered = [u['username'] for u in all_users if query in u['username'].lower()]
                    result_list.set_item_list(filtered)
                
                if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                    selected_user = event.text
                    self.edit_player_screen(selected_user)
                    all_users = api_client.admin_get_users()
                    search_entry.set_text("")
                    result_list.set_item_list([])

                self.MANAGER.process_events(event)

            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN); pygame.display.update()

    def edit_player_screen(self, username):
        status_msg = ""
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(30).render(f"EDIT: {username}", True, RED)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 80)))
            
            if status_msg: self.draw_text(status_msg, self.get_font(20), GREEN, 50, 150)
            
            RESET_PASS = Button(self.button_image, (250, 250), "RESET PASS", self.get_font(30), WHITE, YELLOW)
            DELETE_USER = Button(self.button_image, (250, 370), "DELETE USER", self.get_font(30), WHITE, RED)
            BACK = Button(self.button_image, (250, 600), "BACK", self.get_font(30), WHITE, CYAN)
            
            for b in [RESET_PASS, DELETE_USER, BACK]: b.changeColor(MOUSE); b.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK.checkForInput(MOUSE): return
                    
                    if RESET_PASS.checkForInput(MOUSE):
                        if api_client.admin_reset_password(username, "1234"):
                            status_msg = "Pass reset to '1234'"
                        else: status_msg = "Error"
                        
                    if DELETE_USER.checkForInput(MOUSE):
                        if api_client.admin_delete_user(username):
                            return 
                        else: status_msg = "Error deleting"
                        
            self.clock.tick(FPS); pygame.display.update()

    # --- LOGI SYSTEMOWE ---
    def logs_screen(self):
        logs = api_client.admin_get_logs()
        formatted_logs = [f"[{l['created_at'][11:19]}] {l['event_type']}: {l['message']}" for l in logs]
        
        log_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect((20, 100), (460, 500)),
            item_list=formatted_logs,
            manager=self.MANAGER
        )
        
        while True:
            self.SCREEN.blit(self.background, (0, 0))
            UI_REFRESH = self.clock.tick(60)/1000.0
            MOUSE = pygame.mouse.get_pos()
            
            TITLE = self.get_font(30).render("SYSTEM LOGS", True, YELLOW)
            self.SCREEN.blit(TITLE, TITLE.get_rect(center=(250, 50)))
            
            BACK = Button(self.button_image, (250, 700), "BACK", self.get_font(30), WHITE, CYAN)
            BACK.changeColor(MOUSE); BACK.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK.checkForInput(MOUSE): 
                        log_list.kill(); return
            
                self.MANAGER.process_events(event)
            
            self.MANAGER.update(UI_REFRESH); self.MANAGER.draw_ui(self.SCREEN); pygame.display.update()