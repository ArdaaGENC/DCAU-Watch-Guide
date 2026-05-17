import flet as ft
import json
import os
from core.themes import THEMES
from core.locales import LOCALES

class AppState:
    def __init__(self, db, api, page):
        self.db = db
        self.api = api
        self.page = page
        self._listeners = []
        self.settings_file = os.path.join("data", "settings.json")
        self.theme_mode = "dark"
        self.theme_name = "gold"
        self.language = "en"
        self._load_preferences()

    def _load_preferences(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.theme_mode = data.get("theme_mode", "dark")
                    self.theme_name = data.get("theme_name", "gold")
                    self.language = data.get("language", "en")
            except:
                pass
        self.apply_theme()

    def _save_preferences(self):
        data = {
            "theme_mode": self.theme_mode,
            "theme_name": self.theme_name,
            "language": self.language
        }
        try:
            if not os.path.exists("data"):
                os.makedirs("data")
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except:
            pass

    def t(self, key):
        return LOCALES.get(self.language, LOCALES["en"]).get(key, key)

    def t_uni(self, uni_name):
        return self.db.get_universe_translation(uni_name, self.language)

    def subscribe(self, listener):
        self._listeners.append(listener)

    def navigate(self, tab_index, show_data=None):
        for listener in self._listeners:
            listener({"action": "NAVIGATE", "index": tab_index, "data": show_data})

    def refresh_data(self):
        for listener in self._listeners:
            listener({"action": "DATA_CHANGED"})

    def set_theme_mode(self, mode):
        self.theme_mode = mode
        self._save_preferences()
        self.apply_theme()

    def set_theme_name(self, name):
        self.theme_name = name
        self._save_preferences()
        self.apply_theme()

    def set_language(self, lang):
        self.language = lang
        self._save_preferences()
        self.refresh_data()

    def apply_theme(self):
        self.page.theme_mode = ft.ThemeMode.DARK if self.theme_mode == "dark" else ft.ThemeMode.LIGHT
        is_dark = (self.theme_mode == "dark")
        theme_data = THEMES.get(self.theme_name, THEMES["gold"])

        custom_scheme = ft.ColorScheme(
            primary=theme_data["primary"],
            on_primary=theme_data["on_primary"],
            surface="#121212" if is_dark else "#ffffff",
            on_surface="#ffffff" if is_dark else "#000000",
            surface_container_highest="#1e1e1e" if is_dark else "#eaeaea",
            on_surface_variant="#aaaaaa" if is_dark else "#555555"
        )
        self.page.theme = ft.Theme(color_scheme=custom_scheme)
        self.page.bgcolor = "#0e0e0e" if is_dark else "#f5f5f5"
        
        if getattr(self, "page", None):
            try:
                self.page.update()
            except:
                pass