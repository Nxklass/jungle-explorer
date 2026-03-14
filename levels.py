import pygame
import os
import logging
import math
from jungle_explorer.config import BASE_WIDTH, BASE_HEIGHT, ASSETS_DIR
from jungle_explorer.assets import PLATFORM_IMAGE, GROUND1_IMAGE, GOAL_IMAGE, ENEMY_FRAMES, MOVING_PLATFORM_IMAGE, get_scaled_image

class Platform(pygame.sprite.Sprite):
    """Eine Plattform im Spiel."""
    def __init__(self, x: int, y: int, width: int, height: int, image_path: str, is_ground: bool = False):
        super().__init__()
        self.image = get_scaled_image(image_path, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_ground = is_ground

class MovingPlatform(Platform):
    """Eine bewegliche Plattform zwischen zwei Punkten."""
    def __init__(self, x: int, y: int, width: int, height: int, image_path: str, min_x: int, max_x: int, speed: float):
        super().__init__(x, y, width, height, image_path)
        self.min_x = min_x
        self.max_x = max_x
        self.speed = speed
        self.velocity_x = speed  # Startet nach rechts
        self.delta_x = 0
        self.is_ground = False  # Bewegliche Plattformen gelten nicht als Boden
        # Nur der obere Bereich zählt für Kollisionen
        collision_height = int(150 * (height / 381))  # 150px anteilig zur Bildhöhe
        self.collision_rect = pygame.Rect(x, y, width, collision_height)

    def update(self, dt: float) -> None:
        """Aktualisiert Position und Kollisionsrechteck der Plattform."""
        previous_x = self.rect.x
        self.rect.x += int(self.velocity_x * dt)
        if self.rect.left < self.min_x:
            self.rect.left = self.min_x
            self.velocity_x = abs(self.speed)
        elif self.rect.right > self.max_x:
            self.rect.right = self.max_x
            self.velocity_x = -abs(self.speed)
        self.delta_x = self.rect.x - previous_x
        # Kollisionsrechteck auf Bildposition synchronisieren
        self.collision_rect.topleft = self.rect.topleft

class Enemy(pygame.sprite.Sprite):
    """Ein patrouillierender Gegner mit Animation."""
    def __init__(self, x: int, y: int, min_x: int, max_x: int):
        super().__init__()
        self.frames = ENEMY_FRAMES
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.min_x = min_x
        self.max_x = max_x
        self.velocity_x = 100  # Horizontale Geschwindigkeit
        self.velocity_y = 0
        self.gravity = 1500
        self.on_ground = False
        self.platform = None
        self.animation_speed = 0.2
        self.animation_timer = 0
        self.facing_right = True  # Richtung für Sprite-Ausrichtung

    def apply_gravity(self, dt: float) -> None:
        if not self.on_ground:
            self.velocity_y += self.gravity * dt
        else:
            self.velocity_y = 0

    def move(self, dt: float) -> None:
        # Horizontale Patrouille
        self.rect.x += int(self.velocity_x * dt)
        if self.rect.left < self.min_x:
            self.rect.left = self.min_x
            self.velocity_x = abs(self.velocity_x)
            self.facing_right = True
        elif self.rect.right > self.max_x:
            self.rect.right = self.max_x
            self.velocity_x = -abs(self.velocity_x)
            self.facing_right = False

        # Vertikale Bewegung
        self.rect.y += int(self.velocity_y * dt)

    def check_collisions(self, platforms: pygame.sprite.Group) -> None:
        self.on_ground = False
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        self.platform = None
        for platform in collisions:
            # Bewegliche Plattformen nutzen ein eigenes Kollisionsrechteck
            collision_rect = platform.collision_rect if isinstance(platform, MovingPlatform) else platform.rect
            if self.velocity_y >= 0 and self.rect.bottom >= collision_rect.top - 5:
                if self.rect.left < collision_rect.right and self.rect.right > collision_rect.left:
                    self.rect.bottom = collision_rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.platform = platform
            elif self.velocity_y < 0 and self.rect.top <= collision_rect.bottom:
                self.rect.top = collision_rect.bottom
                self.velocity_y = 0

        # Gegner unter die Bodenlinie verhindern
        ground_level = 720  # Entspricht BASE_HEIGHT
        if self.rect.bottom >= ground_level:
            self.rect.bottom = ground_level
            self.velocity_y = 0
            self.on_ground = True

    def animate(self, dt: float) -> None:
        self.animation_timer += self.animation_speed * (60 * dt)  # Auf 60 FPS normieren
        if self.animation_timer >= 1:
            self.animation_timer -= 1
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
        # Sprite je nach Richtung spiegeln
        if not self.facing_right:
            self.image = pygame.transform.flip(self.frames[self.current_frame], True, False)
        else:
            self.image = self.frames[self.current_frame]

    def update(self, platforms: pygame.sprite.Group, dt: float) -> None:
        self.apply_gravity(dt)
        self.move(dt)
        self.check_collisions(platforms)
        self.animate(dt)

class Goal(pygame.sprite.Sprite):
    """Das Ziel, das der Spieler erreichen muss."""
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = get_scaled_image(GOAL_IMAGE, (80, 80))
        self.rect = self.image.get_rect(topleft=(x, y))

def load_level(level_num: int, base_width: int, base_height: int, scale: float) -> tuple:
    """Lädt Plattformen, Gegner, Ziele und Startposition eines Levels."""
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    goals = pygame.sprite.Group()
    player_start = (100, 500)

    if level_num == 1:
        # Bodenplattform
        platforms.add(Platform(0, base_height - 85, base_width, 50, GROUND1_IMAGE, is_ground=True))
        # Schwebende Plattformen
        platforms.add(Platform(200, 515, 170, 30, PLATFORM_IMAGE))  # Erste Plattform
        platforms.add(Platform(450, 405, 170, 30, PLATFORM_IMAGE))  # Zweite Plattform
        platforms.add(Platform(900, 405, 170, 30, PLATFORM_IMAGE))  # Dritte Plattform
        platforms.add(Platform(1050, 285, 170, 30, PLATFORM_IMAGE)) # Vierte Plattform
        platforms.add(Platform(700, 200, 170, 30, PLATFORM_IMAGE))  # Fünfte Plattform
        # Bewegliche Plattform zwischen mittleren Ebenen
        platforms.add(MovingPlatform(620, 405, 100, 30, MOVING_PLATFORM_IMAGE, min_x=620, max_x=900, speed=100))
        # Gegner läuft auf der ersten Plattform
        enemies.add(Enemy(300, 360, 200, 370))
        # Zielposition
        goals.add(Goal(1095, 210))

    elif level_num == 2:
        # Bodenplattform
        platforms.add(Platform(0, base_height - 50, base_width, 50, PLATFORM_IMAGE, is_ground=True))
        # Komplexere Plattformanordnung
        platforms.add(Platform(200, 450, 150, 20, PLATFORM_IMAGE))
        platforms.add(Platform(400, 350, 150, 20, PLATFORM_IMAGE))
        platforms.add(Platform(600, 250, 150, 20, PLATFORM_IMAGE))
        # Zwei Gegner
        enemies.add(Enemy(200, 410, 150, 350))
        enemies.add(Enemy(600, 210, 550, 750))
        # Zielposition
        goals.add(Goal(1100, 200))
        player_start = (50, 500)

    else:
        logging.error("Invalid level number: %d", level_num)
        raise ValueError(f"Level {level_num} not defined")

    return platforms, enemies, goals, player_start