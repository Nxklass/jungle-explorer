import pygame
import os
import logging
from jungle_explorer.config import ASSETS_DIR
from typing import Tuple

# Zwischenspeicher für bereits skalierte Bilder
SCALED_IMAGES = {}

def get_scaled_image(path: str, size: Tuple[int, int]) -> pygame.Surface:
    """Lädt ein Bild, skaliert es und cached das Ergebnis."""
    key = (path, size)
    if key not in SCALED_IMAGES:
        try:
            image = pygame.image.load(path).convert_alpha()
            scaled_image = pygame.transform.scale(image, size)
            SCALED_IMAGES[key] = scaled_image
            logging.info("Loaded and scaled image: %s to size %s", path, size)
        except pygame.error as error:
            logging.error("Error loading image %s: %s", path, error)
            fallback = pygame.Surface(size)
            fallback.fill((255, 0, 0))  # Gut sichtbarer Platzhalter bei Fehlern
            SCALED_IMAGES[key] = fallback
    return SCALED_IMAGES[key]

# Spieler-Assets
PLAYER_FRAMES = []
frame_names = ["player_run_1.png", "player_run_2.png", "player_run_3.png", "player_run_4.png"]
for frame_name in frame_names:
    frame_path = os.path.join(ASSETS_DIR, frame_name)
    frame = get_scaled_image(frame_path, (50, 60))
    PLAYER_FRAMES.append(frame)

JUMP_FRAME_PATH = os.path.join(ASSETS_DIR, "player_jump.png")
JUMP_FRAME = get_scaled_image(JUMP_FRAME_PATH, (50, 60))

# Gegner-Assets
ENEMY_FRAMES = []
enemy_frame_names = ["enemy_run_1.png", "enemy_run_2.png"]
for frame_name in enemy_frame_names:
    frame_path = os.path.join(ASSETS_DIR, frame_name)
    frame = get_scaled_image(frame_path, (40, 40))
    ENEMY_FRAMES.append(frame)

# Plattform- und Ziel-Assets
PLATFORM_IMAGE = os.path.join(ASSETS_DIR, "platform.png")
GROUND1_IMAGE = os.path.join(ASSETS_DIR, "ground_platform1.png")
GOAL_IMAGE = os.path.join(ASSETS_DIR, "goal.png")
MOVING_PLATFORM_IMAGE = os.path.join(ASSETS_DIR, "moving_platform.png")