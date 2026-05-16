import flet as ft

class StatsTab(ft.Container):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.padding = 20
        self.expand = True
        self.visible = False
        self.content_col = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.content = self.content_col
        self.state.subscribe(self._on_message)

    def did_mount(self):
        self._build_view()

    def _on_message(self, msg):
        if msg.get("action") == "DATA_CHANGED":
            self._build_view()
        elif msg.get("action") == "NAVIGATE" and msg.get("index") == 4:
            self._build_view()

    def _build_view(self):
        data = self.state.db.get_analytics()
        self.content_col.controls.clear()

        movies_count = data.get("watched_movies", 0)
        shows_count = data.get("watched_shows", 0)

        movie_card = ft.Container(
            content=ft.Column([
                ft.Text(f"🎬 {self.state.t('movies')}", size=16, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.BOLD),
                ft.Text(str(movies_count), size=28, color=ft.Colors.PRIMARY, weight=ft.FontWeight.BOLD)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, padding=20, border_radius=10, expand=True
        )

        show_card = ft.Container(
            content=ft.Column([
                ft.Text(f"📺 {self.state.t('shows')}", size=16, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.BOLD),
                ft.Text(str(shows_count), size=28, color=ft.Colors.PRIMARY, weight=ft.FontWeight.BOLD)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, padding=20, border_radius=10, expand=True
        )

        distribution_row = ft.Row([movie_card, show_card], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

        chart_column = ft.Column(spacing=10)
        time_per_uni = data.get("universe_watch_time", {})
        
        if time_per_uni:
            max_time = max(time_per_uni.values()) if time_per_uni.values() else 1
            sorted_unis = sorted(time_per_uni.items(), key=lambda x: x[1], reverse=True)
            
            for uni, minutes in sorted_unis:
                hours = minutes / 60
                pct = minutes / max_time
                bar_width = int(pct * 250)
                
                bar_container = ft.Container(
                    width=bar_width if bar_width > 5 else 5,
                    height=20,
                    bgcolor=ft.Colors.PRIMARY,
                    border_radius=5
                )

                row = ft.Row([
                    ft.Text(uni[:15], width=110, text_align=ft.TextAlign.RIGHT, size=13),
                    bar_container,
                    ft.Text(f"{hours:.1f} {self.state.t('hours')}", size=13, color=ft.Colors.ON_SURFACE_VARIANT)
                ], alignment=ft.MainAxisAlignment.START)

                chart_column.controls.append(row)
        else:
            chart_column.controls.append(ft.Text(self.state.t("no_data_yet"), color=ft.Colors.ON_SURFACE_VARIANT))

        chart_panel = ft.Container(
            content=ft.Column([
                ft.Text(self.state.t("time_spent_per_universe"), size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                ft.Divider(color=ft.Colors.OUTLINE_VARIANT),
                chart_column
            ]),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, padding=20, border_radius=10, width=500
        )

        self.content_col.controls.extend([
            ft.Text(self.state.t("watch_distribution"), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
            distribution_row,
            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
            chart_panel
        ])

        if getattr(self, "page", None):
            try:
                self.update()
            except Exception: pass