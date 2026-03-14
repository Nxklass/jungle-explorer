import pygame
import time
from typing import Dict, Tuple, Callable
import logging
from jungle_explorer.config import (
    GAME_BACKGROUND, BASE_WIDTH, BASE_HEIGHT, save_config, SCALE, DEATH_SCREEN_DURATION
)
from jungle_explorer.player import Player
from jungle_explorer.levels import Platform, Enemy, Goal, load_level, MovingPlatform
from jungle_explorer.menus import Menu, LevelSelectMenu, SettingsMenu, PauseMenu, StatsMenu, DeathScreen
from jungle_explorer.progress import load_progress, save_progress, reset_progress, save_stats, format_time

def handle_menu(
    game_state: Dict, event_list: list, game_surface: pygame.Surface, dt: float
) -> Tuple[str, int | None]:
    """Verarbeitet den Zustand des Hauptmenüs."""
    menu = game_state["menu"]
    progress = game_state["progress"]
    menu.draw(progress, game_surface)
    for event in event_list:
        if event.type == pygame.MOUSEBUTTONDOWN:
            result = menu.check_click(event.pos, progress)
            if result == "level_select":
                game_state["stats"]["last_start_time"] = time.time()
                save_stats(game_state["stats"])
                return "level_select", None
            elif result == "stats":
                return "stats", None
            elif result == "settings":
                return "settings", None
            elif result == "quit":
                return "quit", None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                menu.selected_index = (menu.selected_index - 1) % len(menu.buttons)
            elif event.key == pygame.K_DOWN:
                menu.selected_index = (menu.selected_index + 1) % len(menu.buttons)
            elif event.key == pygame.K_RETURN:
                action = menu.buttons[menu.selected_index]["action"]
                if action == "level_select":
                    game_state["stats"]["last_start_time"] = time.time()
                    save_stats(game_state["stats"])
                    return "level_select", None
                elif action == "stats":
                    return "stats", None
                elif action == "settings":
                    return "settings", None
                elif action == "quit":
                    return "quit", None
    return game_state["state"], game_state["current_level"]

def handle_level_select(
    game_state: Dict, event_list: list, game_surface: pygame.Surface, dt: float
) -> Tuple[str, int | None]:
    """Verarbeitet den Zustand der Levelauswahl."""
    level_menu = game_state["level_select_menu"]
    progress = game_state["progress"]
    settings_menu = game_state["settings_menu"]
    if settings_menu.dev_mode:
        progress["levels"]["1"] = "unlocked"
        progress["levels"]["2"] = "unlocked"
    level_menu.draw(progress, game_surface)
    for event in event_list:
        if event.type == pygame.MOUSEBUTTONDOWN:
            result = level_menu.check_click(event.pos, progress)
            if result == "play_level_1":
                return "playing", 1
            elif result == "play_level_2":
                return "playing", 2
            elif result == "back":
                game_state["stats"]["total_playtime"] += time.time() - game_state["stats"]["last_start_time"]
                game_state["stats"]["last_start_time"] = None
                save_stats(game_state["stats"])
                return "menu", None
            elif result == "reset_progress":
                game_state["progress"] = reset_progress()
                save_progress(game_state["progress"])
                return "level_select", None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level_menu.selected_index = (level_menu.selected_index - 1) % len(level_menu.buttons)
            elif event.key == pygame.K_DOWN:
                level_menu.selected_index = (level_menu.selected_index + 1) % len(level_menu.buttons)
            elif event.key == pygame.K_RETURN:
                action = level_menu.buttons[level_menu.selected_index]["action"]
                if action == "play_level_1" and (progress["levels"]["1"] == "unlocked" or settings_menu.dev_mode):
                    return "playing", 1
                elif action == "play_level_2" and (progress["levels"]["2"] == "unlocked" or settings_menu.dev_mode):
                    return "playing", 2
                elif action == "back":
                    game_state["stats"]["total_playtime"] += time.time() - game_state["stats"]["last_start_time"]
                    game_state["stats"]["last_start_time"] = None
                    save_stats(game_state["stats"])
                    return "menu", None
                elif action == "reset_progress":
                    game_state["progress"] = reset_progress()
                    save_progress(game_state["progress"])
                    return "level_select", None
            elif event.key == pygame.K_ESCAPE:
                game_state["stats"]["total_playtime"] += time.time() - game_state["stats"]["last_start_time"]
                game_state["stats"]["last_start_time"] = None
                save_stats(game_state["stats"])
                return "menu", None
    return game_state["state"], game_state["current_level"]

def handle_settings(
    game_state: Dict, event_list: list, game_surface: pygame.Surface, dt: float
) -> Tuple[str, int | None]:
    """Verarbeitet den Zustand der Einstellungen."""
    settings_menu = game_state["settings_menu"]
    settings_menu.draw(game_surface)
    settings_menu.handle_input(event_list)
    for event in event_list:
        if event.type == pygame.MOUSEBUTTONDOWN:
            result = settings_menu.check_click(event.pos)
            if result == "back":
                return "menu" if game_state["game_sprites"] is None else "paused", None
            settings_menu.update_slider(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            settings_menu.dragging = None
        elif event.type == pygame.MOUSEMOTION and settings_menu.dragging is not None:
            settings_menu.update_slider(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_config(settings_menu.music_volume / 100, settings_menu.sfx_volume / 100, settings_menu.dev_mode)
                return "menu" if game_state["game_sprites"] is None else "paused", None
            settings_menu.handle_navigation(event.key)
    return game_state["state"], game_state["current_level"]

def handle_playing(
    game_state: Dict, event_list: list, game_surface: pygame.Surface, dt: float
) -> Tuple[str, int | None]:
    """Verarbeitet den laufenden Spielzustand."""
    if game_state["game_sprites"] is None:
        platforms, enemies, goals, player_start = load_level(
            game_state["current_level"], BASE_WIDTH, BASE_HEIGHT, SCALE
        )
        player = Player(*player_start)
        game_state["platforms"] = platforms
        game_state["enemies"] = enemies
        game_state["goals"] = goals
        game_state["game_sprites"] = pygame.sprite.Group(player, platforms, enemies, goals)
        game_state["player"] = player
        game_state["start_time"] = time.time()

    player = game_state["player"]
    platforms = game_state["platforms"]
    enemies = game_state["enemies"]
    goals = game_state["goals"]

    for event in event_list:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "paused", game_state["current_level"]

    for platform in platforms:
        if isinstance(platform, MovingPlatform):
            platform.update(dt)

    try:
        player.update(platforms, dt, event_list)
    except Exception as e:
        logging.error("Error in player.update: %s", str(e))
        raise

    for enemy in enemies:
        enemy.update(platforms, dt)

    if pygame.sprite.spritecollide(player, enemies, False):
        game_state["game_sprites"] = None
        game_state["stats"]["total_playtime"] += time.time() - game_state["start_time"]
        save_stats(game_state["stats"])
        game_state["death_screen"].reset(time.time())
        return "death", None

    if pygame.sprite.spritecollide(player, goals, False):
        playtime = time.time() - game_state["start_time"]
        if game_state["current_level"] < 2:
            game_state["progress"]["levels"][str(game_state["current_level"] + 1)] = "unlocked"
            save_progress(game_state["progress"])
        if (game_state["stats"]["best_times"][str(game_state["current_level"])] is None or
            playtime < game_state["stats"]["best_times"][str(game_state["current_level"])]):
            game_state["stats"]["best_times"][str(game_state["current_level"])] = playtime
        game_state["stats"]["total_playtime"] += playtime
        game_state["stats"]["last_start_time"] = None
        save_stats(game_state["stats"])
        game_state["game_sprites"] = None
        return "menu", None

    game_surface.blit(GAME_BACKGROUND, (0, 0))
    game_state["game_sprites"].draw(game_surface)

    return game_state["state"], game_state["current_level"]

def handle_paused(
    game_state: Dict, event_list: list, game_surface: pygame.Surface, dt: float
) -> Tuple[str, int | None]:
    """Verarbeitet den pausierten Zustand."""
    game_surface.blit(GAME_BACKGROUND, (0, 0))
    game_state["game_sprites"].draw(game_surface)
    pause_menu = game_state["pause_menu"]
    pause_menu.draw(game_surface)
    for event in event_list:
        if event.type == pygame.MOUSEBUTTONDOWN:
            result = pause_menu.check_click(event.pos)
            if result == "continue":
                return "playing", game_state["current_level"]
            elif result == "settings":
                return "settings", game_state["current_level"]
            elif result == "home":
                game_state["game_sprites"] = None
                game_state["stats"]["total_playtime"] += time.time() - game_state["start_time"]
                game_state["stats"]["last_start_time"] = None
                save_stats(game_state["stats"])
                return "menu", None
            elif result == "quit":
                return "quit", None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "playing", game_state["current_level"]
    return game_state["state"], game_state["current_level"]

def handle_stats(
    game_state: Dict, event_list: list, game_surface: pygame.Surface, dt: float
) -> Tuple[str, int | None]:
    """Verarbeitet den Statistikzustand."""
    stats_menu = game_state["stats_menu"]
    stats = game_state["stats"]
    stats_menu.draw(stats, game_surface)
    for event in event_list:
        if event.type == pygame.MOUSEBUTTONDOWN:
            result = stats_menu.check_click(event.pos)
            if result == "back":
                return "menu", None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu", None
    return game_state["state"], game_state["current_level"]

def handle_death(
    game_state: Dict, event_list: list, game_surface: pygame.Surface, dt: float
) -> Tuple[str, int | None]:
    """Verarbeitet den Zustand des Todesscreens."""
    death_screen = game_state["death_screen"]
    current_time = time.time()

    # Spielhintergrund und Sprites zeichnen
    game_surface.blit(GAME_BACKGROUND, (0, 0))
    if game_state["game_sprites"]:
        game_state["game_sprites"].draw(game_surface)
    
    # Todesscreen zeichnen
    death_screen.draw(game_surface)
    
    # Überspringen per ESC prüfen
    if death_screen.check_escape(event_list):
        pygame.mixer.music.unpause()  # Hintergrundmusik fortsetzen
        return "menu", None
    
    # Ende der Animation prüfen
    if death_screen.is_finished(current_time):
        pygame.mixer.music.unpause()  # Hintergrundmusik fortsetzen
        return "menu", None
    
    return game_state["state"], game_state["current_level"]