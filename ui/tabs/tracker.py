import flet as ft

class HoverContainer(ft.Container):
    def __init__(self, content, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.shape = ft.BoxShape.CIRCLE
        self.bgcolor = ft.Colors.TRANSPARENT
        self.animate_color = 300
        self.on_hover = self._handle_hover

    def _handle_hover(self, e):
        self.bgcolor = "#26FFFFFF" if e.data == "true" else ft.Colors.TRANSPARENT
        self.update()

class TrackerTab(ft.Container):
    def __init__(self, switch_func, db, api, auto_select_show=None):
        super().__init__()
        self.switch_func = switch_func
        self.db = db   
        self.api = api 
        self.alignment = ft.Alignment(0, 0)
        self.padding = 30
        self.expand = True

        self.progress_ring = ft.ProgressRing(value=0, stroke_width=8, width=90, height=90, color=ft.Colors.AMBER)
        self.progress_text = ft.Text("0%", size=18, weight=ft.FontWeight.BOLD)
        
        self.stat_watched = ft.Text("Watched: 0 / 0", size=15, weight=ft.FontWeight.BOLD)
        self.stat_remaining = ft.Text("Remaining Shows: 0", size=14, color=ft.Colors.WHITE70)
        self.stat_time = ft.Text("Remaining Time: 0 Hours 0 Mins", size=14, color=ft.Colors.GREEN)

        ring_stack = ft.Stack([
            self.progress_ring,
            ft.Container(self.progress_text, alignment=ft.Alignment(0, 0), width=90, height=90)
        ])

        stats_panel = ft.Container(
            content=ft.Row([
                ring_stack,
                ft.Column([
                    self.stat_watched,
                    self.stat_remaining,
                    self.stat_time
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=25)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=25),
            padding=15, bgcolor="#2a2a2a", border_radius=15, width=400
        )

        self.uni_drop = ft.Dropdown(width=400, label="Universe", on_select=self._on_universe_change)

        self.filter_drop = ft.Dropdown(
            options=[
                ft.DropdownOption(key="all", text="All Types"),
                ft.DropdownOption(key="movie", text="Movies Only"),
                ft.DropdownOption(key="show", text="Shows Only")
            ],
            value="all", width=190, label="Filter", on_select=self._on_filter_change
        )
        
        self.sort_drop = ft.Dropdown(
            options=[
                ft.DropdownOption(key="chrono", text="Chronological"),
                ft.DropdownOption(key="release", text="Release Order")
            ],
            value="chrono", width=190, label="Sort", on_select=self._on_filter_change
        )
        
        filter_sort_row = ft.Row([self.filter_drop, self.sort_drop], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        self.show_drop = ft.Dropdown(width=400, label="Last Watched / Current Show", on_select=self._on_show_change)
        
        self.poster_img = ft.Image(src="", width=170, height=240, fit=ft.BoxFit.COVER, border_radius=10, visible=False)
        
        self.main_fav_btn = ft.IconButton(
            icon=ft.Icons.FAVORITE_BORDER,
            icon_color=ft.Colors.WHITE,
            icon_size=25,
            on_click=self._toggle_main_fav
        )
        self.main_fav_wrapper = HoverContainer(content=self.main_fav_btn, right=5, top=5)
        self.main_fav_wrapper.visible = False

        self.main_rate_btn = ft.PopupMenuButton(
            icon=ft.Icons.STAR_BORDER,
            icon_color=ft.Colors.WHITE,
            icon_size=25,
            items=[ft.PopupMenuItem(content=ft.Text("Clear"), data=0, on_click=self._on_rate_change)] +
                  [ft.PopupMenuItem(content=ft.Text(f"{i} ⭐"), data=i, on_click=self._on_rate_change) for i in range(1, 11)]
        )
        self.main_rate_wrapper = HoverContainer(content=self.main_rate_btn, left=5, top=5)
        self.main_rate_wrapper.visible = False

        self.rate_badge = ft.Container(
            content=ft.Text("", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            bgcolor="#CC000000",
            padding=ft.Padding(left=6, top=2, right=6, bottom=2),
            border_radius=5,
            left=5, top=45,
            visible=False
        )

        self.main_ctx_menu = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.OPEN_IN_NEW,
                icon_color=ft.Colors.WHITE,
                icon_size=40,
                on_click=self._open_main_tmdb
            ),
            bgcolor="#AA000000",
            alignment=ft.Alignment(0, 0),
            width=170, height=240, border_radius=10,
            visible=False
        )
        
        self.poster_detector = ft.GestureDetector(
            on_secondary_tap=self._toggle_main_ctx,
            on_tap=self._handle_main_tap,
            content=ft.Stack(
                controls=[
                    self.poster_img,
                    self.main_fav_wrapper,
                    self.main_rate_wrapper,
                    self.rate_badge,
                    self.main_ctx_menu
                ],
                width=170, height=240
            )
        )
        
        self.recommendations_container = ft.Container()

        self.content = ft.Column([
            stats_panel,       
            self.uni_drop,     
            filter_sort_row,   
            self.show_drop,    
            self.poster_detector,
            self.recommendations_container 
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, scroll=ft.ScrollMode.ADAPTIVE)

        self._init_data(auto_select_show)

    def _init_data(self, auto_select_show):
        timeline_data = self.db.load_timeline()
        universes = list(timeline_data.keys())
        self.uni_drop.options = [ft.DropdownOption(key=u, text=u) for u in universes]
        
        initial_uni = universes[0] if universes else None
        if auto_select_show:
            for u, shows in timeline_data.items():
                for item in shows:
                    title = item if isinstance(item, str) else item.get("title")
                    if auto_select_show == title:
                        initial_uni = u
                        break
                        
        self.uni_drop.value = initial_uni
        self._update_dashboard(is_initial=True)

    def set_show(self, data):
        timeline_data = self.db.load_timeline()
        for u, shows in timeline_data.items():
            for item in shows:
                title = item if isinstance(item, str) else item.get("title")
                if data == title:
                    self.uni_drop.value = u
                    self.db.save_progress(u, data)
                    self._update_dashboard(is_initial=False)
                    return

    def _on_universe_change(self, e):
        if e: e.control.value = e.data
        self._update_dashboard(is_initial=False)

    def _on_filter_change(self, e):
        if e: e.control.value = e.data
        self._update_dashboard(is_initial=False)

    def _on_show_change(self, e):
        if e: e.control.value = e.data
        self.db.save_progress(self.uni_drop.value, self.show_drop.value)
        self._update_dashboard(is_initial=False)

    def _toggle_main_fav(self, e):
        title = self.show_drop.value
        uni = self.uni_drop.value
        timeline_data = self.db.load_timeline()
        raw_shows = timeline_data.get(uni, [])
        item_type = "show"
        
        for item in raw_shows:
            if isinstance(item, dict) and item.get("title") == title:
                item_type = item.get("type", "show")
                break
            elif isinstance(item, str) and title in item:
                item_type = "movie" if "(Film)" in item else "show"
                break
                
        is_fav = self.db.toggle_favorite(title, item_type, uni)
        self.main_fav_btn.icon = ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER
        self.main_fav_btn.icon_color = ft.Colors.RED if is_fav else ft.Colors.WHITE
        self.update()

    def _on_rate_change(self, e):
        score = e.control.data
        title = self.show_drop.value
        if title:
            self.db.set_rating(title, score)
            self._update_dashboard(is_initial=False)

    def _toggle_rec_fav(self, e, title, item_type):
        is_fav = self.db.toggle_favorite(title, item_type, "Unknown")
        e.control.icon = ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER
        e.control.icon_color = ft.Colors.RED if is_fav else ft.Colors.WHITE
        self.update()

    def _on_rec_rate(self, e, title):
        self.db.set_rating(title, e.control.data)
        self._update_dashboard(is_initial=False)

    def _toggle_main_ctx(self, e):
        self.main_ctx_menu.visible = not self.main_ctx_menu.visible
        self.update()

    def _handle_main_tap(self, e):
        if self.main_ctx_menu.visible:
            self.main_ctx_menu.visible = False
            self.update()

    def _open_main_tmdb(self, e):
        self.main_ctx_menu.visible = False
        self.update()
        if self.show_drop.value:
            det = self.api.fetch_show_details(self.show_drop.value)
            if det and det.get("tmdb_id"):
                m_type = det.get("media_type", "movie")
                url = f"https://www.themoviedb.org/{m_type}/{det['tmdb_id']}"
                
                async def launch():
                    await e.page.launch_url(url)
                e.page.run_task(launch)

    def _toggle_ctx_menu(self, e, menu_container):
        menu_container.visible = not menu_container.visible
        self.update()

    def _handle_rec_tap(self, e, title, menu_container):
        if menu_container.visible:
            menu_container.visible = False
            self.update()
        else:
            self.switch_func(0, title)

    def _open_rec_tmdb(self, e):
        e.control.parent.visible = False
        self.update()
        title = e.control.data
        if title:
            det = self.api.fetch_show_details(title)
            if det and det.get("tmdb_id"):
                m_type = det.get("media_type", "movie")
                url = f"https://www.themoviedb.org/{m_type}/{det['tmdb_id']}"
                
                async def launch():
                    await e.page.launch_url(url)
                e.page.run_task(launch)

    def _update_dashboard(self, is_initial=False):
        current_uni = self.uni_drop.value
        if not current_uni: return
        
        timeline_data = self.db.load_timeline()
        raw_shows = timeline_data.get(current_uni, [])
        
        processed = []
        for item in raw_shows:
            if isinstance(item, str):
                processed.append({"title": item, "type": "all", "chrono": 0, "release": 0, "runtime_min": 0})
            else:
                processed.append(item)
                
        current_filter = self.filter_drop.value
        if current_filter and current_filter != "all":
            processed = [s for s in processed if s.get("type", "all").lower() == current_filter]
            
        current_sort = self.sort_drop.value
        if current_sort == "chrono":
            processed = sorted(processed, key=lambda x: x.get("chrono", 0))
        elif current_sort == "release":
            processed = sorted(processed, key=lambda x: x.get("release", 0))
            
        filtered_titles = [s["title"] for s in processed]
        self.show_drop.options = [ft.DropdownOption(key=t, text=t) for t in filtered_titles]
        
        prog = self.db.load_progress()
        saved_show = prog.get(current_uni)
        
        if saved_show and saved_show in filtered_titles:
            self.show_drop.value = saved_show
        else:
            self.show_drop.value = filtered_titles[0] if filtered_titles else None

        stats = self.db.get_dynamic_stats(processed, self.show_drop.value)
        if stats:
            pct = stats["percentage"]
            self.progress_ring.value = pct / 100.0  
            self.progress_text.value = f"{int(pct)}%"
            self.stat_watched.value = f"Watched: {stats['watched_count']} / {stats['total_items']}"
            self.stat_remaining.value = f"Remaining Shows: {stats['remaining_items']}"
            self.stat_time.value = f"Remaining Time: {stats['remaining_time_str']}"

        if self.show_drop.value:
            det = self.api.fetch_show_details(self.show_drop.value)
            is_fav = self.db.is_favorite(self.show_drop.value)
            score = self.db.get_rating(self.show_drop.value)
            
            self.main_fav_btn.icon = ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER
            self.main_fav_btn.icon_color = ft.Colors.RED if is_fav else ft.Colors.WHITE
            self.main_fav_wrapper.visible = True

            self.main_rate_wrapper.visible = True
            if score > 0:
                self.main_rate_btn.icon = ft.Icons.STAR
                self.main_rate_btn.icon_color = ft.Colors.AMBER
                self.rate_badge.content.value = f"{score}/10"
                self.rate_badge.visible = True
            else:
                self.main_rate_btn.icon = ft.Icons.STAR_BORDER
                self.main_rate_btn.icon_color = ft.Colors.WHITE
                self.rate_badge.visible = False
            
            if det and det.get("image_url"):
                self.poster_img.src = det.get("image_url")
                self.poster_img.visible = True
            else:
                self.poster_img.visible = False
                
            tmdb_id = det.get("tmdb_id")
            media_type = det.get("media_type", "movie")
            self.recommendations_container.content = self._build_recommendations_ui(tmdb_id, media_type)
        else:
            self.recommendations_container.content = ft.Container()
            self.main_fav_wrapper.visible = False
            self.main_rate_wrapper.visible = False
            self.rate_badge.visible = False
            self.poster_img.visible = False

        if not is_initial:
            try:
                if self.page: self.page.update()
            except Exception: pass

    def _build_recommendations_ui(self, tmdb_id, media_type):
        recs = self.api.get_recommendations(tmdb_id, media_type)
        
        if not recs:
            return ft.Container() 

        rec_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=15)
        
        for rec in recs:
            img_src = rec.get("image")
            title = rec.get("title")
            rec_type = rec.get("type", "movie")
            
            is_fav = self.db.is_favorite(title)
            score = self.db.get_rating(title)
            
            fav_btn = ft.IconButton(
                icon=ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER,
                icon_color=ft.Colors.RED if is_fav else ft.Colors.WHITE,
                icon_size=16,
                on_click=lambda e, t=title, typ=rec_type: self._toggle_rec_fav(e, t, typ)
            )
            fav_hover = HoverContainer(content=fav_btn, right=0, top=0)

            rate_btn = ft.PopupMenuButton(
                icon=ft.Icons.STAR if score > 0 else ft.Icons.STAR_BORDER,
                icon_color=ft.Colors.AMBER if score > 0 else ft.Colors.WHITE,
                icon_size=16,
                items=[ft.PopupMenuItem(content=ft.Text("Clear"), data=0, on_click=lambda e, t=title: self._on_rec_rate(e, t))] +
                      [ft.PopupMenuItem(content=ft.Text(f"{i} ⭐"), data=i, on_click=lambda e, t=title: self._on_rec_rate(e, t)) for i in range(1, 11)]
            )
            rate_hover = HoverContainer(content=rate_btn, left=0, top=0)

            rate_badge = ft.Container(
                content=ft.Text(f"{score}", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                bgcolor="#CC000000",
                padding=ft.Padding(left=4, top=2, right=4, bottom=2),
                border_radius=5,
                left=5, top=30,
                visible=score > 0
            )

            rec_ctx_menu = ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.OPEN_IN_NEW,
                    icon_color=ft.Colors.WHITE,
                    icon_size=30,
                    data=title,
                    on_click=self._open_rec_tmdb
                ),
                bgcolor="#AA000000",
                alignment=ft.Alignment(0, 0),
                width=100, height=150, border_radius=8,
                visible=False
            )
            
            card_detector = ft.GestureDetector(
                on_secondary_tap=lambda e, m=rec_ctx_menu: self._toggle_ctx_menu(e, m),
                on_tap=lambda e, t=title, m=rec_ctx_menu: self._handle_rec_tap(e, t, m),
                content=ft.Stack(
                    controls=[
                        ft.Image(
                            src=img_src, 
                            width=100, 
                            height=150, 
                            fit=ft.BoxFit.COVER, 
                            border_radius=8
                        ) if img_src else ft.Container(
                            width=100, 
                            height=150, 
                            bgcolor="#333333", 
                            border_radius=8
                        ),
                        fav_hover,
                        rate_hover,
                        rate_badge,
                        rec_ctx_menu
                    ],
                    width=100, height=150
                )
            )
            
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        card_detector,
                        ft.Text(
                            title, 
                            size=12, 
                            text_align=ft.TextAlign.CENTER, 
                            max_lines=2, 
                            width=100,
                            overflow=ft.TextOverflow.ELLIPSIS
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                ),
                tooltip=title
            )
            rec_row.controls.append(card)

        return ft.Column(
            controls=[
                ft.Divider(height=20, color=ft.Colors.WHITE24),
                ft.Text("Similar Shows", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER),
                rec_row
            ],
            spacing=10
        )