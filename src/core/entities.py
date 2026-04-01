import pygame
import random
from src.core.config import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, screen, image_path=None):
        super(Tile, self).__init__()
        
        tile_size = random.randint(0, 2)
        if tile_size == 0:
            self.tile_w = 85
            self.tile_h = 125
        elif tile_size == 1:
            self.tile_w = 105
            self.tile_h = 155
        else:
            self.tile_w = 125
            self.tile_h = 190
        
        self.shape = random.choice(["rectangle", "circle", "triangle"])
        self.screen = screen
        self.x, self.y = x, y
        self.color = BLACK
        self.alive = True
        
        self.surface = pygame.Surface((self.tile_w, self.tile_h), pygame.SRCALPHA)
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.image = None
        if image_path and self.shape == "rectangle":
            try:
                if not os.path.isabs(image_path) and not image_path.startswith("assets"):
                     full_path = os.path.join(ASSETS_DIR, os.path.basename(image_path))
                else:
                     full_path = image_path
                
                self.image = pygame.image.load(full_path)
                self.image = pygame.transform.scale(self.image, (self.tile_w, self.tile_h))
            except pygame.error as e:
                print(f"Błąd ładowania obrazka: {image_path} - {e}")
    
    def update(self, speed, border_color):
        self.rect.y += speed
        if self.rect.y >= HEIGHT:
            self.kill()
        
        if self.alive:
            if self.shape == 'rectangle':
                if self.image:
                    self.surface.blit(self.image, (0, 0))
                else:
                    pygame.draw.rect(self.surface, self.color, (0, 0, self.tile_w, self.tile_h))
                pygame.draw.rect(self.surface, border_color, (0, 0, self.tile_w, self.tile_h), 2)
            elif self.shape == "circle":
                center = (self.tile_w // 2, self.tile_h // 2)
                radius = min(self.tile_w, self.tile_h) // 2
                pygame.draw.circle(self.surface, self.color, center, radius)
                pygame.draw.circle(self.surface, border_color, center, radius, 2)
            elif self.shape == "triangle":
                points = [(self.tile_w // 2, self.tile_h), (0, 0), (self.tile_w, 0)]
                pygame.draw.polygon(self.surface, self.color, points)
                pygame.draw.polygon(self.surface, border_color, points, 2)
        else:
            if self.shape == "rectangle":
                pygame.draw.rect(self.surface, (0, 0, 0, 90), (0, 0, self.tile_w, self.tile_h))
            elif self.shape == "circle":
                center = (self.tile_w // 2, self.tile_h // 2)
                radius = min(self.tile_w, self.tile_h) // 2
                pygame.draw.circle(self.surface, (0, 0, 0, 90), center, radius)
            elif self.shape == "triangle":
                points = [(self.tile_w // 2, self.tile_h), (0, 0), (self.tile_w, 0)]
                pygame.draw.polygon(self.surface, (0, 0, 0, 90), points)
            
        self.screen.blit(self.surface, self.rect)
        
    def check_collision(self, pos):
            if self.shape == "rectangle":
                return self.rect.collidepoint(pos)
            elif self.shape == "circle":
                center = (self.rect.x + self.tile_w // 2, self.rect.y + self.tile_h // 2)
                radius = min(self.tile_w, self.tile_h) // 2
                distance = ((pos[0] - center[0]) ** 2 + (pos[1] - center[1]) ** 2) ** 0.5
                return distance <= radius
            elif self.shape == "triangle":
                point1 = (self.rect.x + self.tile_w // 2, self.rect.y + self.tile_h)
                point2 = (self.rect.x, self.rect.y)
                point3 = (self.rect.x + self.tile_w, self.rect.y)
                def sign(p1, p2, p3):
                    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
                b1 = sign(pos, point1, point2) < 0.0
                b2 = sign(pos, point2, point3) < 0.0
                b3 = sign(pos, point3, point1) < 0.0
                return b1 == b2 == b3
            return False