import flet as ft
import asyncio

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

class ShimmerSkeleton(ft.Container):
    def __init__(self):
        super().__init__()
        self.width = 120
        self.height = 180
        self.bgcolor = "#222222"
        self.border_radius = 10
        self.animate = ft.Animation(duration=800, curve=ft.AnimationCurve.EASE_IN_OUT)
        self.alignment = ft.Alignment(0, 0)
        self.content = ft.Text("🎞️", size=30, color="#444444")
        self._is_mounted = False

    def did_mount(self):
        self._is_mounted = True
        self.page.run_task(self._pulsate)

    def will_unmount(self):
        self._is_mounted = False

    async def _pulsate(self):
        while self._is_mounted:
            self.bgcolor = "#3a3a3a" if self.bgcolor == "#222222" else "#222222"
            try:
                self.update()
            except:
                pass
            await asyncio.sleep(0.8)

class FavoritesTab(ft.Container):
    def __init__(self, switch_func, db, api):
        super().__init__()
        self.switch_func = switch_func
        self.db = db
        self.api = api
        self.expand = True
        self.padding = 20
        self._pending_posters = []

        self.filter_drop = ft.Dropdown(
            label="Filter",
            options=[
                ft.DropdownOption(key="all", text="All"),
                ft.DropdownOption(key="movie", text="Movies"),
                ft.DropdownOption(key="show", text="Shows")
            ],
            value="all",
            width=200,
            on_select=self._refresh_view
        )

        self.group_drop = ft.Dropdown(
            label="Group By",
            options=[
                ft.DropdownOption(key="none", text="None"),
                ft.DropdownOption(key="universe", text="Universe")
            ],
            value="none",
            width=200,
            on_select=self._refresh_view
        )

        self.controls_row = ft.Row([self.filter_drop, self.group_drop], alignment=ft.MainAxisAlignment.CENTER)
        self.content_col = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE, spacing=20)
        self.content = ft.Column([self.controls_row, self.content_col], expand=True)

    def did_mount(self):
        self._build_view()

    def _refresh_view(self, e=None):
        if e:
            e.control.value = e.data
        self._build_view()

    def _toggle_ctx_menu(self, e, menu_container):
        menu_container.visible = not menu_container.visible
        self.update()

    def _handle_tap(self, e, title, menu_container):
        if menu_container.visible:
            menu_container.visible = False
            self.update()
        else:
            self.switch_func(0, title)

    def _open_tmdb(self, e, title):
        e.control.parent.visible = False
        self.update()
        det = self.api.fetch_show_details(title)
        if det and det.get("tmdb_id"):
            m_type = det.get("media_type", "movie")
            url = f"https://www.themoviedb.org/{m_type}/{det['tmdb_id']}"
            
            async def launch():
                await e.page.launch_url(url)
            e.page.run_task(launch)

    def _build_view(self):
        favs = self.db.load_favorites()
        timeline = self.db.load_timeline()
        self.content_col.controls.clear()
        self._pending_posters.clear()

        f_val = self.filter_drop.value
        filtered_favs = {}
        for k, v in favs.items():
            current_uni = self._get_current_universe(k, timeline)
            v["universe"] = current_uni
            
            if f_val == "all" or v.get("type", "show") == f_val:
                filtered_favs[k] = v

        if not filtered_favs:
            self.content_col.controls.append(
                ft.Container(
                    content=ft.Text("No favorites found.", color=ft.Colors.WHITE70, size=16),
                    alignment=ft.Alignment(0, 0),
                    expand=True
                )
            )
            self.update()
            return

        g_val = self.group_drop.value
        
        if g_val == "none":
            grid = ft.GridView(max_extent=160, child_aspect_ratio=0.6, spacing=15, run_spacing=15)
            for k, v in filtered_favs.items():
                grid.controls.append(self._create_card(v))
            self.content_col.controls.append(grid)
        else:
            grouped = {}
            for k, v in filtered_favs.items():
                uni = v.get("universe", "Unknown")
                if uni not in grouped:
                    grouped[uni] = []
                grouped[uni].append(v)
            
            for uni, items in grouped.items():
                self.content_col.controls.append(ft.Text(uni, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER))
                grid = ft.GridView(max_extent=160, child_aspect_ratio=0.6, spacing=15, run_spacing=15)
                for v in items:
                    grid.controls.append(self._create_card(v))
                self.content_col.controls.append(grid)

        self.update()
        if self._pending_posters:
            self.page.run_task(self._load_pending_posters)

    def _get_current_universe(self, title, timeline):
        for uni, items in timeline.items():
            for item in items:
                item_title = item if isinstance(item, str) else item.get("title")
                if item_title == title:
                    return uni
        return "Unknown"

    def _create_card(self, item):
        title = item["title"]
        cached_det = self.api._cache.get(title)

        skeleton = ShimmerSkeleton()
        img = ft.Image(src="", fit=ft.BoxFit.COVER, width=120, height=180, visible=False, border_radius=10)
        icon = ft.Text("🎬", size=35, color="white54", visible=False)

        if cached_det:
            skeleton.visible = False
            if cached_det.get("local_image_path"):
                img.src = cached_det.get("local_image_path")
                img.visible = True
            elif cached_det.get("image_url"):
                img.src = cached_det.get("image_url")
                img.visible = True
            else:
                icon.visible = True
        else:
            self._pending_posters.append((title, skeleton, img, icon))

        fav_btn = ft.IconButton(
            icon=ft.Icons.FAVORITE,
            icon_color=ft.Colors.RED,
            icon_size=20,
            on_click=lambda e, t=title, typ=item.get("type", "show"), u=item.get("universe", "Unknown"): self._toggle_fav(e, t, typ, u)
        )
        fav_hover = HoverContainer(content=fav_btn, right=0, top=0)

        score = self.db.get_rating(title)
        rate_btn = ft.PopupMenuButton(
            icon=ft.Icons.STAR if score > 0 else ft.Icons.STAR_BORDER,
            icon_color=ft.Colors.AMBER if score > 0 else ft.Colors.WHITE,
            icon_size=20,
            items=[ft.PopupMenuItem(content=ft.Text("Clear"), data=0, on_click=lambda e, t=title: self._on_rate(e, t))] +
                  [ft.PopupMenuItem(content=ft.Text(f"{i} ⭐"), data=i, on_click=lambda e, t=title: self._on_rate(e, t)) for i in range(1, 11)]
        )
        rate_hover = HoverContainer(content=rate_btn, left=0, top=0)

        rate_badge = ft.Container(
            content=ft.Text(f"{score}", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            bgcolor="#CC000000",
            padding=ft.Padding(left=5, top=2, right=5, bottom=2),
            border_radius=5,
            left=5, top=35,
            visible=score > 0
        )

        fav_ctx_menu = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.OPEN_IN_NEW,
                icon_color=ft.Colors.WHITE,
                icon_size=35,
                data=title,
                on_click=lambda e, t=title: self._open_tmdb(e, t)
            ),
            bgcolor="#AA000000",
            alignment=ft.Alignment(0, 0),
            width=120, height=180, border_radius=10,
            visible=False
        )

        detector = ft.GestureDetector(
            on_secondary_tap=lambda e, m=fav_ctx_menu: self._toggle_ctx_menu(e, m),
            on_tap=lambda e, s=title, m=fav_ctx_menu: self._handle_tap(e, s, m),
            content=ft.Stack(
                controls=[
                    skeleton,
                    img,
                    ft.Container(icon, alignment=ft.Alignment(0, 0), width=120, height=180),
                    fav_hover,
                    rate_hover,
                    rate_badge,
                    fav_ctx_menu
                ]
            )
        )

        img_container = ft.Container(
            width=120, height=180, bgcolor="#333333", border_radius=10,
            content=detector
        )

        return ft.Container(
            content=ft.Column([
                img_container,
                ft.Text(
                    title,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    size=13,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    def _toggle_fav(self, e, title, item_type, universe):
        self.db.toggle_favorite(title, item_type, universe)
        self._build_view()

    def _on_rate(self, e, title):
        self.db.set_rating(title, e.control.data)
        self._build_view()

    async def _load_pending_posters(self):
        pending = list(self._pending_posters)
        self._pending_posters.clear()

        results = await asyncio.gather(
            *[asyncio.to_thread(self.api.fetch_show_details, title) for title, _, _, _ in pending]
        )

        for (title_str, skeleton, img, icon), det in zip(pending, results):
            skeleton.visible = False
            
            if det and det.get("local_image_path"):
                img.src = det["local_image_path"]
                img.visible = True
            elif det and det.get("image_url"):
                img.src = det["image_url"]
                img.visible = True
            else:
                icon.visible = True

        self.update()