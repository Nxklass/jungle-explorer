import os
import logging
import pygame
import json
from typing import Tuple

# Datenverzeichnis anlegen
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    logging.info("Data directory created: %s", DATA_DIR)

# Logging initialisieren
LOG_FILE = os.path.join(DATA_DIR, 'game.log')
with open(LOG_FILE, 'w', encoding='utf-8') as log_file:
    log_file.write('')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)
logging.info("Logging successfully initialized")

# Pygame initialisieren
pygame.init()
pygame.mixer.init()
logging.info("Pygame successfully initialized")

# Basisauflösung (720p)
BASE_WIDTH, BASE_HEIGHT = 1280, 720
WIDTH, HEIGHT = BASE_WIDTH, BASE_HEIGHT
SCALE = 1.0
FPS = 60

# Einstellungen für den Todesscreen
DEATH_SCREEN_DURATION = 3.0  # Dauer in Sekunden

# Fenster mit VSync erstellen
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE, vsync=1)
pygame.display.set_caption("Jungle Explorer")

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
HOVER_COLOR = (255, 215, 0)
HIGHLIGHT_COLOR = (180, 180, 180)
LOCKED_COLOR = (50, 50, 50)
RED = (255, 0, 0)  # Farbe für den Todestext

# Verzeichnis für Assets
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# Hintergrundbilder laden und skalieren
MENU_BG_PATH = os.path.join(ASSETS_DIR, "jungle_background.jpg")
try:
    MENU_BACKGROUND = pygame.image.load(MENU_BG_PATH)
    MENU_BACKGROUND = pygame.transform.scale(MENU_BACKGROUND, (BASE_WIDTH, BASE_HEIGHT))
    logging.info("Menu background image loaded: %s", MENU_BG_PATH)
except pygame.error as error:
    logging.error("Error loading menu background image: %s", error)
    MENU_BACKGROUND = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    MENU_BACKGROUND.fill(BLACK)

GAME_BG_PATH = os.path.join(ASSETS_DIR, "game_background.png")
try:
    GAME_BACKGROUND = pygame.image.load(GAME_BG_PATH)
    GAME_BACKGROUND = pygame.transform.scale(GAME_BACKGROUND, (BASE_WIDTH, BASE_HEIGHT))
    logging.info("Game background image loaded: %s", GAME_BG_PATH)
except pygame.error as error:
    logging.error("Error loading game background image: %s", error)
    GAME_BACKGROUND = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    GAME_BACKGROUND.fill(BLACK)

# Audio laden
MUSIC_PATH = os.path.join(ASSETS_DIR, "background_music.mp3")
try:
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.play(-1)  # Endlosschleife
    logging.info("Background music loaded: %s", MUSIC_PATH)
except pygame.error as error:
    logging.error("Error loading background music: %s", error)

JUMP_SOUND_PATH = os.path.join(ASSETS_DIR, "jump_sound.wav")
try:
    JUMP_SOUND = pygame.mixer.Sound(JUMP_SOUND_PATH)
    logging.info("Jump sound loaded: %s", JUMP_SOUND_PATH)
except pygame.error as error:
    logging.error("Error loading jump sound: %s", error)
    JUMP_SOUND = None

DEATH_SOUND_PATH = os.path.join(ASSETS_DIR, "death_sound.wav")
try:
    DEATH_SOUND = pygame.mixer.Sound(DEATH_SOUND_PATH)
    logging.info("Death sound loaded: %s", DEATH_SOUND_PATH)
except pygame.error as error:
    logging.warning("Death sound not found, using silent placeholder: %s", error)
    DEATH_SOUND = None

def load_config() -> Tuple[float, float, bool]:
    """Lädt Lautstärken und Dev-Modus aus der Konfigurationsdatei."""
    default_config = {"music_volume": 0.5, "sfx_volume": 0.5, "dev_mode": False}
    config_path = os.path.join(DATA_DIR, "config.json")
    try:
        with open(config_path, "r", encoding='utf-8') as config_file:
            config = json.load(config_file)
            music_volume = max(0.0, min(1.0, config.get("music_volume", 0.5)))
            sfx_volume = max(0.0, min(1.0, config.get("sfx_volume", 0.5)))
            dev_mode = config.get("dev_mode", False)
            logging.info("Config loaded: music_volume=%f, sfx_volume=%f, dev_mode=%s", music_volume, sfx_volume, dev_mode)
            return music_volume, sfx_volume, dev_mode
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error("Error loading config.json: %s, using defaults", e)
        with open(config_path, "w", encoding='utf-8') as config_file:
            json.dump(default_config, config_file)
        return 0.5, 0.5, False

def save_config(music_volume: float, sfx_volume: float, dev_mode: bool) -> None:
    """Speichert Lautstärken und Dev-Modus in die Konfigurationsdatei."""
    config = {"music_volume": music_volume, "sfx_volume": sfx_volume, "dev_mode": dev_mode}
    try:
        with open(os.path.join(DATA_DIR, "config.json"), "w", encoding='utf-8') as config_file:
            json.dump(config, config_file)
        logging.info("Config saved: %s", config)
    except Exception as e:
        logging.error("Error saving config: %s", e)

# Startwerte für Lautstärke und Dev-Modus
MUSIC_VOLUME, SFX_VOLUME, DEV_MODE = load_config()
pygame.mixer.music.set_volume(MUSIC_VOLUME)
if JUMP_SOUND:
    JUMP_SOUND.set_volume(SFX_VOLUME)
if DEATH_SOUND:
    DEATH_SOUND.set_volume(SFX_VOLUME)