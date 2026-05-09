import flet as ft
from ui.tabs.tracker import create_tracker_tab
from ui.tabs.library import create_library_tab

def run():
    def main(page: ft.Page):
        page.title = "Universal Tracker"
        page.window.width = 550
        page.window.height = 800
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#1a1a1a"
        page.horizontal_alignment = "center"

        title = ft.Text("🎬 Universal Tracker", size=26, weight="bold", color="amber")

        def switch_to_tab(index, data=None):
            tabs.selected_index = index
            if data and index == 0:
                tab_view.controls[0] = create_tracker_tab(page, switch_to_tab, data)
            if page:
                page.update()

        tab_view = ft.TabBarView(
            expand=True,
            controls=[
                create_tracker_tab(page, switch_to_tab),
                create_library_tab(page, switch_to_tab)
            ]
        )

        tabs = ft.Tabs(
            selected_index=0,
            length=2,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Tracker"),
                            ft.Tab(label="Library"),
                        ]
                    ),
                    tab_view
                ]
            )
        )

        page.add(title, tabs)

    ft.app(target=main)