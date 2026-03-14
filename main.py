import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pygame
import time
from typing import Dict, Callable
from jungle_explorer import (
    WIDTH, HEIGHT, WINDOW, MENU_BACKGROUND, GAME_BACKGROUND, SCALE, FPS, BLACK,
    Menu, LevelSelectMenu, SettingsMenu, PauseMenu, StatsMenu, DeathScreen,
    load_progress, load_stats, save_stats,
    handle_menu, handle_level_select, handle_settings, handle_playing, handle_paused, handle_stats, handle_death,
    BASE_WIDTH, BASE_HEIGHT
)
from jungle_explorer.levels import Platform, Enemy, Goal, load_level

def main() -> None:
    """Hauptspielschleife."""
    game_state = {
        "width": WIDTH,
        "height": HEIGHT,
        "window": WINDOW,
        "menu_background": MENU_BACKGROUND,
        "game_background": GAME_BACKGROUND,
        "scale": SCALE,
        "state": "menu",
        "current_level": None,
        "progress": load_progress(),
        "stats": load_stats(),
        "menu": Menu(),
        "settings_menu": SettingsMenu(),
        "pause_menu": PauseMenu(),
        "level_select_menu": LevelSelectMenu(),
        "stats_menu": StatsMenu(),
        "death_screen": DeathScreen(),
        "game_sprites": None,
        "platforms": None,
        "enemies": None,
        "goals": None,
        "player": None,
        "start_time": None
    }

    state_handlers: Dict[str, Callable] = {
        "menu": handle_menu,
        "level_select": handle_level_select,
        "settings": handle_settings,
        "playing": handle_playing,
        "paused": handle_paused,
        "stats": handle_stats,
        "death": handle_death
    }

    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 20)  # Schrift für FPS-Anzeige

    while running:
        dt = clock.tick(FPS) / 1000
        game_state["window"].fill(BLACK)
        game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                running = False
                if game_state["stats"]["last_start_time"] is not None:
                    game_state["stats"]["total_playtime"] += time.time() - game_state["stats"]["last_start_time"]
                    game_state["stats"]["last_start_time"] = None
                    save_stats(game_state["stats"])
                break

        if not running:
            break

        new_state, new_level = state_handlers[game_state["state"]](
            game_state, event_list, game_surface, dt
        )
        game_state["state"] = new_state
        game_state["current_level"] = new_level

        if game_state["state"] == "quit":
            running = False

        game_state["window"].blit(game_surface, (0, 0))
        
        # FPS-Overlay nur im Dev-Modus zeichnen
        if game_state["settings_menu"].dev_mode:
            fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
            game_state["window"].blit(fps_text, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    print("Starting Jungle Explorer...")
    main()