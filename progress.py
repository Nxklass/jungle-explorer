import json
import os
import time
import logging
from typing import Dict
from jungle_explorer.config import DATA_DIR

def load_progress() -> Dict:
    """Lädt den Spielfortschritt aus einer Datei."""
    default_progress = {"levels": {"1": "unlocked", "2": "locked"}}
    try:
        with open(os.path.join(DATA_DIR, "progress.json"), "r", encoding='utf-8') as progress_file:
            progress = json.load(progress_file)
            # Struktur des Fortschritts prüfen
            if "levels" not in progress or not all(str(i) in progress["levels"] for i in [1, 2]):
                logging.warning("Invalid progress.json, using default progress")
                return default_progress
            return progress
    except (FileNotFoundError, json.JSONDecodeError):
        logging.info("No progress file found, creating default progress.json")
        with open(os.path.join(DATA_DIR, "progress.json"), "w", encoding='utf-8') as progress_file:
            json.dump(default_progress, progress_file)
        return default_progress

def save_progress(progress: Dict) -> None:
    """Speichert den Spielfortschritt in eine Datei."""
    try:
        with open(os.path.join(DATA_DIR, "progress.json"), "w", encoding="utf-8") as progress_file:
            json.dump(progress, progress_file)
        logging.info("Progress saved: %s", progress)
    except Exception as e:
        logging.error("Error saving progress: %s", e)

def reset_progress() -> Dict:
    """Setzt den Spielfortschritt auf Standardwerte zurück."""
    default_progress = {"levels": {"1": "unlocked", "2": "locked"}}
    try:
        with open(os.path.join(DATA_DIR, "progress.json"), "w", encoding='utf-8') as progress_file:
            json.dump(default_progress, progress_file)
        logging.info("Progress reset to default: %s", default_progress)
        return default_progress
    except Exception as e:
        logging.error("Error resetting progress: %s", e)
        return default_progress

def load_stats() -> Dict:
    """Lädt Spielstatistiken wie Bestzeiten und Gesamtspielzeit."""
    default_stats = {
        "best_times": {"1": None, "2": None},
        "total_playtime": 0.0,
        "last_start_time": None
    }
    stats_path = os.path.join(DATA_DIR, "stats.json")
    try:
        with open(stats_path, "r", encoding='utf-8') as stats_file:
            stats = json.load(stats_file)
            # Struktur der Statistikdaten prüfen
            if not all(key in stats for key in ["best_times", "total_playtime", "last_start_time"]):
                logging.warning("Invalid stats.json, using default stats")
                return default_stats
            return stats
    except (FileNotFoundError, json.JSONDecodeError):
        logging.info("No stats file found, creating default stats.json")
        with open(stats_path, "w", encoding='utf-8') as stats_file:
            json.dump(default_stats, stats_file)
        return default_stats

def save_stats(stats: Dict) -> None:
    """Speichert die Spielstatistiken in eine Datei."""
    try:
        with open(os.path.join(DATA_DIR, "stats.json"), "w", encoding='utf-8') as stats_file:
            json.dump(stats, stats_file)
        logging.info("Stats saved: %s", stats)
    except Exception as e:
        logging.error("Error saving stats: %s", e)

def format_time(seconds: float) -> str:
    """Formatiert Sekunden in das Format MM:SS.mmm."""
    if seconds is None:
        return "Nicht abgeschlossen"
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"