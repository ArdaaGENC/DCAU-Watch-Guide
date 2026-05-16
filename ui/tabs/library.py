import flet as ft
import asyncio
from ui.components.show_card import ShowCard

class LibraryTab(ft.Container):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.expand = True
        self.padding = 20
        self._pending_posters = []
        self.state.subscribe(self._on_message)

        self.grid = ft.GridView(expand=True, max_extent=160, child_aspect_ratio=0.6, spacing=15)

        timeline_data = self.state.db.load_timeline()
        self.universes = list(timeline_data.keys())
        initial_uni = self.universes[0] if self.universes else None

        self.uni_drop = ft.Dropdown(
            label=self.state.t("universe"),
            options=[ft.DropdownOption(key=u, text=u) for u in self.universes],
            value=initial_uni,
            width=300,
            on_select=self._handle_dropdown_select
        )

        self.content = ft.Column([self.uni_drop, self.grid], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        if initial_uni:
            self._build_grid(initial_uni, is_initial=True)

    def _update_texts(self):
        self.uni_drop.label = self.state.t("universe")
        if getattr(self, "page", None):
            try:
                self.update()
            except Exception: pass

    def _on_message(self, msg):
        if msg.get("action") == "DATA_CHANGED":
            self._update_texts()
            if self.uni_drop.value:
                self._build_grid(self.uni_drop.value)

    def _handle_dropdown_select(self, e):
        if e: e.control.value = e.data
        self._build_grid(self.uni_drop.value)

    def _build_grid(self, uni, is_initial=False):
        self._pending_posters = []
        new_cards = []
        timeline_data = self.state.db.load_timeline()

        for item in timeline_data.get(uni, []):
            title = item if isinstance(item, str) else item.get("title", "")
            item_type = item.get("type", "show") if isinstance(item, dict) else ("movie" if "(Film)" in item else "show")
            cached_det = self.state.api._cache.get(title)

            card = ShowCard(
                state=self.state,
                title=title,
                item_type=item_type,
                universe=uni,
                is_fav=self.state.db.is_favorite(title),
                score=self.state.db.get_rating(title),
                is_watchlist=self.state.db.is_watchlist(title),
                width=120,
                height=180,
                initial_img_src=cached_det.get("local_image_path") or cached_det.get("image_url") if cached_det else None,
                show_skeleton=not bool(cached_det)
            )

            if cached_det and not card.img.src:
                card.icon.visible = True
            elif not cached_det:
                self._pending_posters.append((title, card))

            new_cards.append(card)

        self.grid.controls = new_cards

        if not is_initial:
            self.update()
            if self._pending_posters:
                self.state.page.run_task(self._load_posters)

    def did_mount(self):
        if self._pending_posters:
            self.state.page.run_task(self._load_posters)

    async def _load_posters(self):
        for title, card in self._pending_posters:
            det = self.state.api.fetch_show_details(title)
            if det:
                img_url = det.get("local_image_path") or det.get("image_url")
                if img_url:
                    card.img.src = img_url
                    card.img.visible = True
                    if hasattr(card, "skeleton"): card.skeleton.visible = False
                else:
                    card.icon.visible = True
                card.update()