import flet as ft
from core.themes import THEMES

class SettingsModalOverlay(ft.Stack):
    def __init__(self, state):
        super().__init__(expand=True, visible=False)
        self.state = state
        self._build_ui()
        self.state.subscribe(self._on_state_change)

    def _on_state_change(self, msg):
        if msg.get("action") == "DATA_CHANGED":
            self._update_texts()

    def open_modal(self):
        self.theme_switch.value = (self.state.theme_mode == "dark")
        self.color_drop.value = self.state.theme_name
        self.lang_drop.value = self.state.language
        self.visible = True
        self.update()

    def _close_modal(self, e=None):
        self.visible = False
        self.update()

    def _toggle_theme(self, e):
        new_mode = "dark" if e.control.value else "light"
        self.state.set_theme_mode(new_mode)
        self.theme_switch.value = (self.state.theme_mode == "dark")
        self.update()

    def _change_color(self, e):
        self.state.set_theme_name(e.control.value)
        self.color_drop.value = self.state.theme_name
        self.update()

    def _change_language(self, e):
        self.state.set_language(e.control.value)
        self.lang_drop.value = self.state.language
        self.update()

    def _update_texts(self):
        self.title_text.value = self.state.t("settings")
        self.appearance_text.value = self.state.t("appearance")
        self.theme_switch.label = self.state.t("dark_mode")
        self.color_drop.label = self.state.t("custom_theme")
        self.lang_drop.label = self.state.t("language")
        if self.page:
            self.update()

    def _build_ui(self):
        self.theme_switch = ft.Switch(
            label=self.state.t("dark_mode"),
            value=(self.state.theme_mode == "dark"),
            on_change=self._toggle_theme
        )

        dropdown_options = []
        for key, value in THEMES.items():
            dropdown_options.append(ft.DropdownOption(key=key, text=value["name"]))

        self.color_drop = ft.Dropdown(
            label=self.state.t("custom_theme"),
            options=dropdown_options,
            width=250,
            on_select=self._change_color
        )

        lang_options = [
            ft.DropdownOption(key="en", text="English"),
            ft.DropdownOption(key="tr", text="Türkçe")
        ]
        
        self.lang_drop = ft.Dropdown(
            label=self.state.t("language"),
            options=lang_options,
            width=250,
            on_select=self._change_language
        )

        self.title_text = ft.Text(self.state.t("settings"), weight=ft.FontWeight.BOLD, size=18, color="primary")
        self.appearance_text = ft.Text(self.state.t("appearance"), weight=ft.FontWeight.BOLD, color="primary")

        modal_header = ft.Row(
            controls=[
                self.title_text,
                ft.IconButton(icon=ft.Icons.CLOSE, on_click=self._close_modal)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        settings_content = ft.Column(
            controls=[
                self.appearance_text,
                self.theme_switch,
                self.color_drop,
                self.lang_drop
            ],
            spacing=15
        )

        self.modal_box = ft.Container(
            width=400,
            height=400,
            bgcolor="surface",
            border_radius=15,
            padding=20,
            content=ft.Column(
                controls=[
                    modal_header,
                    ft.Divider(height=1),
                    settings_content
                ],
                expand=True
            )
        )

        self.modal_overlay = ft.Container(
            content=self.modal_box,
            bgcolor="#8A000000",
            alignment=ft.Alignment(0, 0),
            expand=True
        )

        self.controls = [self.modal_overlay]