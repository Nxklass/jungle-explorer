import pygame
import time
import logging
import os
from typing import Dict, Tuple
from jungle_explorer.config import (
    MENU_BACKGROUND, HOVER_COLOR, HIGHLIGHT_COLOR, GRAY, WHITE, LOCKED_COLOR,
    BASE_WIDTH, BASE_HEIGHT, MUSIC_VOLUME, SFX_VOLUME, DEV_MODE, JUMP_SOUND,
    save_config, RED, DEATH_SCREEN_DURATION, DEATH_SOUND
)
from jungle_explorer.progress import format_time

class Menu:
    """Hauptmenü des Spiels."""
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 60, bold=True)
        self.selected_index = 0
        self.hovered_index = None
        button_width = 300
        button_height = 60
        button_spacing = 40
        button_count = 4  # Anzahl der Hauptmenü-Buttons
        total_height = button_count * button_height + (button_count - 1) * button_spacing
        start_y = (BASE_HEIGHT - total_height) // 2
        button_x = (BASE_WIDTH - button_width) // 2
        self.buttons = [
            {"text": "PLAY", "rect": pygame.Rect(button_x, start_y, button_width, button_height), "action": "level_select"},
            {"text": "STATS", "rect": pygame.Rect(button_x, start_y + (button_height + button_spacing), button_width, button_height), "action": "stats"},
            {"text": "SETTINGS", "rect": pygame.Rect(button_x, start_y + 2 * (button_height + button_spacing), button_width, button_height), "action": "settings"},
            {"text": "QUIT", "rect": pygame.Rect(button_x, start_y + 3 * (button_height + button_spacing), button_width, button_height), "action": "quit"}
        ]

    def update_hover(self, mouse_pos: Tuple[float, float]) -> None:
        self.hovered_index = None
        for i, button in enumerate(self.buttons):
            hover_rect = button["rect"].inflate(20, 20)
            if hover_rect.collidepoint(mouse_pos):
                self.hovered_index = i
                break

    def draw(self, _: Dict, surface: pygame.Surface) -> None:
        surface.blit(MENU_BACKGROUND, (0, 0))
        self.update_hover(pygame.mouse.get_pos())
        for i, button in enumerate(self.buttons):
            color = WHITE
            text = self.font.render(button["text"], True, color)
            text_rect = text.get_rect(center=button["rect"].center)
            is_hovered = i == self.hovered_index
            is_selected = i == self.selected_index
            if is_hovered:
                pygame.draw.rect(surface, HOVER_COLOR, button["rect"], 0, border_radius=10)
                pygame.draw.rect(surface, WHITE, button["rect"], 3, border_radius=10)
            elif is_selected:
                pygame.draw.rect(surface, HIGHLIGHT_COLOR, button["rect"], 0, border_radius=10)
                pygame.draw.rect(surface, WHITE, button["rect"], 3, border_radius=10)
            else:
                pygame.draw.rect(surface, GRAY, button["rect"], 0, border_radius=10)
                pygame.draw.rect(surface, WHITE, button["rect"], 2, border_radius=10)
            surface.blit(text, text_rect)

    def check_click(self, pos: Tuple[int, int], _: Dict) -> str | None:
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                return button["action"]
        return None

class LevelSelectMenu:
    """Menü zur Levelauswahl."""
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 55, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 43, bold=True)
        self.lock_font = pygame.font.SysFont("Arial", 55, bold=True)
        self.selected_index = 0
        self.hovered_index = None
        button_width = 300
        button_height = 60
        button_spacing = 40
        reset_button_spacing = 80
        button_count = 4
        total_height = (3 * button_height + 2 * button_spacing) + reset_button_spacing + button_height
        start_x = BASE_WIDTH // 2 - button_width // 2
        start_y = (BASE_HEIGHT - total_height) // 2
        self.buttons = [
            {"text": "Level 1", "rect": pygame.Rect(start_x, start_y, button_width, button_height), "action": "play_level_1", "level": 1, "font": self.font},
            {"text": "Level 2", "rect": pygame.Rect(start_x, start_y + button_height + button_spacing, button_width, button_height), "action": "play_level_2", "level": 2, "font": self.font},
            {"text": "Back", "rect": pygame.Rect(start_x, start_y + 2 * (button_height + button_spacing), button_width, button_height), "action": "back", "level": None, "font": self.font},
            {"text": "Reset Progress", "rect": pygame.Rect(start_x, start_y + 3 * button_height + 2 * button_spacing + reset_button_spacing, button_width, button_height), "action": "reset_progress", "level": None, "font": self.small_font}
        ]

    def update_hover(self, mouse_pos: Tuple[float, float]) -> None:
        self.hovered_index = None
        for i, button in enumerate(self.buttons):
            hover_rect = button["rect"].inflate(20, 20)
            if hover_rect.collidepoint(mouse_pos):
                self.hovered_index = i
                break

    def draw(self, progress: Dict, surface: pygame.Surface) -> None:
        surface.blit(MENU_BACKGROUND, (0, 0))
        self.update_hover(pygame.mouse.get_pos())
        for i, button in enumerate(self.buttons):
            is_locked = button["level"] and progress["levels"].get(str(button["level"]), "locked") == "locked"
            is_hovered = i == self.hovered_index
            is_selected = i == self.selected_index
            if is_locked:
                pygame.draw.rect(surface, LOCKED_COLOR, button["rect"], 0, border_radius=10)
                pygame.draw.rect(surface, WHITE, button["rect"], 2, border_radius=10)
                lock_text = self.lock_font.render("Locked", True, WHITE)
                lock_rect = lock_text.get_rect(center=(button["rect"].centerx, button["rect"].top + 28))
                surface.blit(lock_text, lock_rect)
            else:
                if is_hovered:
                    pygame.draw.rect(surface, HOVER_COLOR, button["rect"], 0, border_radius=10)
                    pygame.draw.rect(surface, WHITE, button["rect"], 3, border_radius=10)
                elif is_selected:
                    pygame.draw.rect(surface, HIGHLIGHT_COLOR, button["rect"], 0, border_radius=10)
                    pygame.draw.rect(surface, WHITE, button["rect"], 3, border_radius=10)
                else:
                    pygame.draw.rect(surface, GRAY, button["rect"], 0, border_radius=10)
                    pygame.draw.rect(surface, WHITE, button["rect"], 2, border_radius=10)
                text = button["font"].render(button["text"], True, WHITE)
                text_rect = text.get_rect(center=button["rect"].center)
                surface.blit(text, text_rect)

    def check_click(self, pos: Tuple[int, int], progress: Dict) -> str | None:
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                if button["level"] and progress["levels"].get(str(button["level"]), "locked") == "locked":
                    return None
                return button["action"]
        return None

class SettingsMenu:
    """Einstellungsmenü mit Lautstärke und Dev-Modus."""
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 36, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.music_volume = MUSIC_VOLUME * 100
        self.sfx_volume = SFX_VOLUME * 100
        self.dev_mode = DEV_MODE
        self.dev_code_input = ""
        self.sliders = [
            {"label": "Music Volume", "value": self.music_volume, "rect": pygame.Rect(500, 300, 400, 20), "type": "music"},
            {"label": "SFX Volume", "value": self.sfx_volume, "rect": pygame.Rect(500, 380, 400, 20), "type": "sfx"}
        ]
        self.selected_slider = 0
        self.dragging = None
        button_width = 150
        button_height = 50
        self.back_button = pygame.Rect(50, BASE_HEIGHT - 100, button_width, button_height)
        self.dev_input_rect = pygame.Rect(500, 460, 200, 40)
        self.dev_toggle_rect = pygame.Rect(710, 460, 100, 40)

    def update_slider(self, pos: Tuple[int, int]) -> None:
        if self.dragging is not None:
            slider = self.sliders[self.dragging]
            relative_x = max(0, min(pos[0] - slider["rect"].x, slider["rect"].width))
            slider["value"] = (relative_x / slider["rect"].width) * 100
            if slider["type"] == "music":
                self.music_volume = slider["value"]
                pygame.mixer.music.set_volume(self.music_volume / 100)
            else:
                self.sfx_volume = slider["value"]
                if JUMP_SOUND:
                    JUMP_SOUND.set_volume(self.sfx_volume / 100)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(MENU_BACKGROUND, (0, 0))
        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        for i, slider in enumerate(self.sliders):
            label_text = self.font.render(f"{slider['label']}: {int(slider['value'])}%", True, WHITE)
            label_rect = label_text.get_rect(topleft=(100, slider["rect"].y - 10))
            surface.blit(label_text, label_rect)
            pygame.draw.rect(surface, GRAY, slider["rect"], 0)
            handle_x = slider["rect"].x + (slider["value"] / 100) * slider["rect"].width
            handle_rect = pygame.Rect(handle_x - 10, slider["rect"].y - 10, 20, 40)
            pygame.draw.rect(surface, WHITE if i == self.selected_slider else HOVER_COLOR, handle_rect, 0, border_radius=5)

        pygame.draw.rect(surface, GRAY, self.dev_input_rect, 0, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.dev_input_rect, 2, border_radius=5)
        input_text = self.small_font.render(self.dev_code_input, True, WHITE)
        input_rect = input_text.get_rect(center=self.dev_input_rect.center)
        surface.blit(input_text, input_rect)

        toggle_text = self.small_font.render("Deaktivieren" if self.dev_mode else "Aktivieren", True, WHITE)
        toggle_rect = toggle_text.get_rect(center=self.dev_toggle_rect.center)
        is_hovered = self.dev_toggle_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, HOVER_COLOR if is_hovered else GRAY, self.dev_toggle_rect, 0, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.dev_toggle_rect, 2, border_radius=10)
        surface.blit(toggle_text, toggle_rect)

        back_text = self.small_font.render("Back", True, WHITE)
        back_rect = back_text.get_rect(center=self.back_button.center)
        is_hovered = self.back_button.collidepoint(mouse_pos)
        pygame.draw.rect(surface, HOVER_COLOR if is_hovered else GRAY, self.back_button, 0, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.back_button, 2, border_radius=10)
        surface.blit(back_text, back_rect)

    def handle_input(self, event_list: list) -> None:
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.dev_code_input:
                    if self.dev_code_input == "2222":
                        self.dev_mode = True
                    self.dev_code_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.dev_code_input = self.dev_code_input[:-1]
                elif event.unicode.isdigit() and len(self.dev_code_input) < 4:
                    self.dev_code_input += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.dev_toggle_rect.collidepoint(event.pos):
                    self.dev_mode = not self.dev_mode
                elif self.dev_input_rect.collidepoint(event.pos):
                    pass

    def check_click(self, pos: Tuple[int, int]) -> str | None:
        if self.back_button.collidepoint(pos):
            save_config(self.music_volume / 100, self.sfx_volume / 100, self.dev_mode)
            return "back"
        for i, slider in enumerate(self.sliders):
            handle_x = slider["rect"].x + (slider["value"] / 100) * slider["rect"].width
            handle_rect = pygame.Rect(handle_x - 10, slider["rect"].y - 10, 20, 40)
            if handle_rect.collidepoint(pos):
                self.dragging = i
                self.selected_slider = i
                return None
        if self.dev_input_rect.collidepoint(pos) or self.dev_toggle_rect.collidepoint(pos):
            return None
        return None

    def handle_navigation(self, key: int) -> None:
        if key == pygame.K_UP:
            self.selected_slider = (self.selected_slider - 1) % len(self.sliders)
        elif key == pygame.K_DOWN:
            self.selected_slider = (self.selected_slider + 1) % len(self.sliders)
        elif key == pygame.K_LEFT:
            self.sliders[self.selected_slider]["value"] = max(0, self.sliders[self.selected_slider]["value"] - 5)
            self.update_volume(self.selected_slider)
        elif key == pygame.K_RIGHT:
            self.sliders[self.selected_slider]["value"] = min(100, self.sliders[self.selected_slider]["value"] + 5)
            self.update_volume(self.selected_slider)

    def update_volume(self, slider_index: int) -> None:
        slider = self.sliders[slider_index]
        if slider["type"] == "music":
            self.music_volume = slider["value"]
            pygame.mixer.music.set_volume(self.music_volume / 100)
        else:
            self.sfx_volume = slider["value"]
            if JUMP_SOUND:
                JUMP_SOUND.set_volume(self.sfx_volume / 100)

class PauseMenu:
    """Pausenmenü des Spiels."""
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.hovered_index = None
        button_width = 300
        button_height = 60
        button_spacing = 40
        total_height = 4 * button_height + 3 * button_spacing
        start_x = BASE_WIDTH // 2 - button_width // 2
        start_y = (BASE_HEIGHT - total_height) // 2
        self.buttons = [
            {"text": "CONTINUE", "rect": pygame.Rect(start_x, start_y, button_width, button_height), "action": "continue"},
            {"text": "SETTINGS", "rect": pygame.Rect(start_x, start_y + button_height + button_spacing, button_width, button_height), "action": "settings"},
            {"text": "HOME", "rect": pygame.Rect(start_x, start_y + 2 * (button_height + button_spacing), button_width, button_height), "action": "home"},
            {"text": "QUIT", "rect": pygame.Rect(start_x, start_y + 3 * (button_height + button_spacing), button_width, button_height), "action": "quit"}
        ]

    def update_hover(self, mouse_pos: Tuple[float, float]) -> None:
        self.hovered_index = None
        for i, button in enumerate(self.buttons):
            hover_rect = button["rect"].inflate(20, 20)
            if hover_rect.collidepoint(mouse_pos):
                self.hovered_index = i
                break

    def draw(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        self.update_hover(pygame.mouse.get_pos())
        for i, button in enumerate(self.buttons):
            text = self.font.render(button["text"], True, WHITE)
            text_rect = text.get_rect(center=button["rect"].center)
            is_hovered = i == self.hovered_index
            pygame.draw.rect(surface, HOVER_COLOR if is_hovered else GRAY, button["rect"], 0, border_radius=10)
            pygame.draw.rect(surface, WHITE, button["rect"], 2, border_radius=10)
            surface.blit(text, text_rect)

    def check_click(self, pos: Tuple[int, int]) -> str | None:
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                return button["action"]
        return None

class StatsMenu:
    """Statistikmenü mit Bestzeiten und Gesamtspielzeit."""
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 50, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 30)
        self.back_button = pygame.Rect(50, BASE_HEIGHT - 100, 150, 50)

    def draw(self, stats: Dict, surface: pygame.Surface) -> None:
        surface.blit(MENU_BACKGROUND, (0, 0))
        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        title_text = self.font.render("Statistics", True, WHITE)
        title_rect = title_text.get_rect(center=(BASE_WIDTH // 2, 100))
        surface.blit(title_text, title_rect)

        y_offset = 200
        for level in ["1", "2"]:
            time_text = self.small_font.render(
                f"Level {level}: {format_time(stats['best_times'][level])}",
                True, WHITE
            )
            time_rect = time_text.get_rect(center=(BASE_WIDTH // 2, y_offset))
            surface.blit(time_text, time_rect)
            y_offset += 80

        total_time_text = self.small_font.render(
            f"Gesamte Spielzeit: {time.strftime('%H:%M:%S', time.gmtime(stats['total_playtime']))}",
            True, WHITE
        )
        total_time_rect = total_time_text.get_rect(center=(BASE_WIDTH // 2, y_offset))
        surface.blit(total_time_text, total_time_rect)

        mouse_pos = pygame.mouse.get_pos()
        back_text = self.small_font.render("Back", True, WHITE)
        back_rect = back_text.get_rect(center=self.back_button.center)
        is_hovered = self.back_button.collidepoint(mouse_pos)
        pygame.draw.rect(surface, HOVER_COLOR if is_hovered else GRAY, self.back_button, 0, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.back_button, 2, border_radius=10)
        surface.blit(back_text, back_rect)

    def check_click(self, pos: Tuple[int, int]) -> str | None:
        if self.back_button.collidepoint(pos):
            return "back"
        return None

class DeathScreen:
    """Todesscreen mit Ein- und Ausblendeffekt."""
    def __init__(self):
        # Schriftgröße relativ zur Bildschirmhöhe für gute Lesbarkeit
        font_size = int(BASE_HEIGHT * 0.225)
        # Erst Spezialschrift laden, sonst auf Systemschriftarten ausweichen
        try:
            self.font = pygame.font.Font("jungle_explorer/assets/OptimusPrinceps.ttf", font_size)
            logging.info("Successfully loaded OptimusPrinceps.ttf")
        except Exception as e:
            logging.error(f"Failed to load OptimusPrinceps.ttf: {str(e)}")
            try:
                self.font = pygame.font.SysFont("impact", font_size, bold=False)
                logging.info("Falling back to impact font")
            except Exception as e:
                logging.error(f"Failed to load impact font: {str(e)}")
                self.font = pygame.font.SysFont("arialblack", font_size, bold=False)
                logging.info("Falling back to arialblack font")
        self.text = "YOU DIED"
        self.text_color = (255, 0, 0)  # Reines Rot (#FF0000)
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2))
        self.background = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        self.background.fill((0, 0, 0))  # Schwarzer Hintergrund
        self.start_time = None
        self.fade_in_duration = 1.5  # Sekunden
        self.full_visibility_duration = 2.0  # Sekunden
        self.fade_out_duration = 1.0  # Sekunden
        self.total_duration = self.fade_in_duration + self.full_visibility_duration + self.fade_out_duration
        self.alpha = 0
        self.sound_played = False

    def reset(self, current_time: float) -> None:
        """Setzt den Todesscreen für einen neuen Durchlauf zurück."""
        self.start_time = current_time
        self.alpha = 0
        self.sound_played = False
        # Hintergrundmusik pausieren
        pygame.mixer.music.pause()
        # Todessound abspielen, falls vorhanden
        if DEATH_SOUND and not self.sound_played:
            DEATH_SOUND.play()
            self.sound_played = True

    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet den Todesscreen mit Fade-Animation."""
        try:
            if self.start_time is None:
                return

            current_time = time.time()
            elapsed = current_time - self.start_time

            # Alpha-Wert je nach Animationsphase berechnen
            if elapsed < self.fade_in_duration:
                # Einblenden
                self.alpha = (elapsed / self.fade_in_duration) * 255
            elif elapsed < (self.fade_in_duration + self.full_visibility_duration):
                # Voll sichtbar
                self.alpha = 255
            elif elapsed < self.total_duration:
                # Ausblenden
                fade_out_elapsed = elapsed - (self.fade_in_duration + self.full_visibility_duration)
                self.alpha = 255 * (1 - fade_out_elapsed / self.fade_out_duration)
            else:
                self.alpha = 0

            # Alpha in gültigem Bereich halten
            self.alpha = max(0, min(255, int(self.alpha)))

            # Hintergrund zeichnen
            surface.blit(self.background, (0, 0))
            # Alpha auf Text anwenden
            self.text_surface.set_alpha(self.alpha)
            # Text zeichnen
            surface.blit(self.text_surface, self.text_rect)

        except Exception as e:
            logging.error("Error drawing death screen: %s", str(e))
            raise

    def is_finished(self, current_time: float) -> bool:
        """Prüft, ob die Todesscreen-Animation beendet ist."""
        if self.start_time is None:
            return False
        elapsed = current_time - self.start_time
        if elapsed >= self.total_duration and DEATH_SOUND and self.sound_played:
            DEATH_SOUND.stop()  # Sound nach Animation stoppen
        return elapsed >= self.total_duration

    def check_escape(self, event_list: list) -> bool:
        """Prüft, ob ESC den Todesscreen überspringt."""
        for event in event_list:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if DEATH_SOUND and self.sound_played:
                    DEATH_SOUND.stop()  # Sound beim Überspringen stoppen
                return True
        return False