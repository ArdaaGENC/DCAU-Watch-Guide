import flet as ft

class ManagerModalOverlay(ft.Stack):
    def __init__(self, state):
        super().__init__(expand=True, visible=False)
        self.state = state
        self._build_ui()
        self.state.subscribe(self._on_message)

    def _on_message(self, msg):
        if msg.get("action") == "DATA_CHANGED":
            self._update_texts()

    def _update_texts(self):
        self.search_input.label = self.state.t("search_movies_shows")
        self.del_uni_drop.label = self.state.t("select_universe")
        self.del_show_drop.label = self.state.t("select_show")
        self.new_uni_input.label = self.state.t("new_universe_name")
        
        self.create_uni_txt.value = self.state.t("create_new_universe")
        self.add_uni_btn.text = self.state.t("add_universe")
        self.remove_data_txt.value = self.state.t("remove_data")
        self.del_uni_btn.text = self.state.t("delete_selected_universe")
        self.del_show_btn.text = self.state.t("delete_selected_show")
        
        if self.del_uni_drop.options:
            for opt in self.del_uni_drop.options:
                opt.text = self.state.t_uni(opt.key)
        
        self.dialog_tab_buttons[0].content.value = self.state.t("search_and_add")
        self.dialog_tab_buttons[1].content.value = self.state.t("manage_db_tab")
        
        self.modal_header_txt.value = self.state.t("database_manager")
        self.confirm_header_txt.value = self.state.t("confirm_deletion")
        self.cancel_btn.text = self.state.t("cancel")
        self.confirm_btn.text = self.state.t("delete")

        if getattr(self, "page", None):
            try:
                self.update()
            except Exception: pass

    def open_modal(self):
        self._load_del_drops()
        self.visible = True
        self.update()

    def _close_modal(self, e=None):
        self.visible = False
        self.update()
        self.state.page.floating_action_button.visible = True
        self.state.page.update()

    def _build_ui(self):
        self.search_results_col = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=15, expand=True)
        self.search_input = ft.TextField(label=self.state.t("search_movies_shows"), expand=True, on_submit=self._perform_search)
        search_btn = ft.IconButton(icon=ft.Icons.SEARCH, on_click=self._perform_search)
        search_row = ft.Row([self.search_input, search_btn])

        self.search_tab = ft.Container(
            content=ft.Column([search_row, self.search_results_col], expand=True),
            padding=15, expand=True, visible=True
        )

        self.del_uni_drop = ft.Dropdown(label=self.state.t("select_universe"), width=250, on_select=self._on_del_uni_change)
        self.del_show_drop = ft.Dropdown(label=self.state.t("select_show"), width=250)
        self.new_uni_input = ft.TextField(label=self.state.t("new_universe_name"), width=200)

        self.create_uni_txt = ft.Text(self.state.t("create_new_universe"), weight=ft.FontWeight.BOLD, color="primary")
        self.add_uni_btn = ft.ElevatedButton(self.state.t("add_universe"), on_click=self._add_uni_action)
        self.remove_data_txt = ft.Text(self.state.t("remove_data"), weight=ft.FontWeight.BOLD, color="primary")
        self.del_uni_btn = ft.ElevatedButton(self.state.t("delete_selected_universe"), color="error", on_click=self._delete_uni_action)
        self.del_show_btn = ft.ElevatedButton(self.state.t("delete_selected_show"), color="error", on_click=self._delete_show_action)

        self.manage_tab = ft.Container(
            content=ft.Column([
                self.create_uni_txt,
                ft.Row([self.new_uni_input, self.add_uni_btn]),
                ft.Divider(height=25, color="outlineVariant"),
                self.remove_data_txt,
                self.del_uni_drop,
                self.del_uni_btn,
                ft.Divider(height=15, color="transparent"),
                self.del_show_drop,
                self.del_show_btn
            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=10),
            padding=15, expand=True, visible=False
        )

        def switch_dialog_tab(e):
            idx = e.control.data
            self.search_tab.visible = (idx == 0)
            self.manage_tab.visible = (idx == 1)
            for i, btn in enumerate(self.dialog_tab_buttons):
                btn.border = ft.Border(bottom=ft.BorderSide(2, "primary")) if i == idx else None
                btn.content.color = "primary" if i == idx else "onSurfaceVariant"
            self.update()

        self.dialog_tab_buttons = [
            ft.Container(content=ft.Text(self.state.t("search_and_add"), weight=ft.FontWeight.BOLD, color="primary"), data=0, on_click=switch_dialog_tab, padding=10, border=ft.Border(bottom=ft.BorderSide(2, "primary")), ink=True),
            ft.Container(content=ft.Text(self.state.t("manage_db_tab"), weight=ft.FontWeight.BOLD, color="onSurfaceVariant"), data=1, on_click=switch_dialog_tab, padding=10, ink=True),
        ]
        dialog_tabs_row = ft.Row(self.dialog_tab_buttons, alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        dialog_content_area = ft.Column([self.search_tab, self.manage_tab], expand=True)

        self.modal_header_txt = ft.Text(self.state.t("database_manager"), weight=ft.FontWeight.BOLD, size=18, color="primary")
        modal_header = ft.Row(
            [self.modal_header_txt,
             ft.IconButton(icon=ft.Icons.CLOSE, icon_color="onSurfaceVariant", on_click=self._close_modal)], 
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.modal_overlay = ft.Container(
            content=ft.Container(
                width=500, height=550, bgcolor="surface", border_radius=15, padding=15,
                content=ft.Column([modal_header, dialog_tabs_row, ft.Divider(height=1, color="outlineVariant"), dialog_content_area], expand=True)
            ),
            bgcolor="#CC000000", alignment=ft.Alignment(0, 0), expand=True
        )

        self.confirm_dialog_content = ft.Text("")
        self.confirm_callback_holder = []

        self.confirm_header_txt = ft.Text(self.state.t("confirm_deletion"), weight=ft.FontWeight.BOLD, size=18, color="error")
        self.cancel_btn = ft.TextButton(self.state.t("cancel"), on_click=self._close_confirm_dlg)
        self.confirm_btn = ft.ElevatedButton(self.state.t("delete"), bgcolor="error", color="onError", on_click=self._execute_confirm)

        confirm_dialog_box = ft.Container(
            content=ft.Column([
                self.confirm_header_txt,
                self.confirm_dialog_content,
                ft.Row([
                    self.cancel_btn,
                    self.confirm_btn
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True, spacing=20),
            bgcolor="surfaceContainerHighest", padding=20, border_radius=10, width=400
        )

        self.confirm_overlay = ft.Container(
            content=confirm_dialog_box, bgcolor="#AA000000", alignment=ft.Alignment(0, 0), expand=True, visible=False
        )

        self.controls = [self.modal_overlay, self.confirm_overlay]

    def _perform_search(self, e=None):
        self.search_results_col.controls.clear()
        self.search_results_col.controls.append(ft.ProgressRing())
        self.update()
        
        query = self.search_input.value
        if not query:
            self.search_results_col.controls.clear()
            self.update()
            return
            
        results = self.state.api.search_tmdb_query(query)
        self.search_results_col.controls.clear()
        
        if not results:
            self.search_results_col.controls.append(ft.Text(self.state.t("no_results_tmdb"), color="onSurfaceVariant"))
            self.update()
            return
        
        universes = list(self.state.db.load_timeline().keys())
        
        for res in results:
            uni_dropdown = ft.Dropdown(options=[ft.DropdownOption(key=u, text=self.state.t_uni(u)) for u in universes], width=110, hint_text=self.state.t("universe"), text_size=12)
            chrono_input = ft.TextField(label=self.state.t("order"), width=60, text_size=12, keyboard_type=ft.KeyboardType.NUMBER)
            
            def add_clicked(e, r=res, d=uni_dropdown, c_inp=chrono_input):
                if not d.value: return
                release_year = int(r['year']) if r['year'] else 0
                c_val = int(c_inp.value) if c_inp.value and c_inp.value.isdigit() else None
                    
                self.state.db.add_show(d.value, r['title'], r['type'], c_val, release_year, 0)
                self.state.refresh_data()
                
                d.disabled = True
                c_inp.disabled = True
                e.control.disabled = True
                e.control.icon = ft.Icons.CHECK
                e.control.icon_color = "green"
                self.update()

            add_btn = ft.IconButton(icon=ft.Icons.ADD, icon_color="primary", on_click=add_clicked)
            image_control = ft.Image(src=res['image'], width=40, height=60, fit=ft.BoxFit.COVER, border_radius=5) if res['image'] else ft.Container(width=40, height=60, bgcolor="surfaceVariant", border_radius=5)
            
            row = ft.Row([
                image_control,
                ft.Column([
                    ft.Text(res['title'], weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"{res['type'].capitalize()} • {res['year']}", size=11, color="onSurfaceVariant")
                ], spacing=2, expand=True),
                uni_dropdown, chrono_input, add_btn
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            
            self.search_results_col.controls.append(row)
        self.update()

    def _load_del_drops(self):
        timeline = self.state.db.load_timeline()
        unis = list(timeline.keys())
        
        self.del_uni_drop.options = [ft.DropdownOption(key=u, text=self.state.t_uni(u)) for u in unis]
        
        if not self.del_uni_drop.value or self.del_uni_drop.value not in unis:
            self.del_uni_drop.value = unis[0] if unis else None
        
        if self.del_uni_drop.value:
            shows = timeline.get(self.del_uni_drop.value, [])
            show_titles = [s["title"] for s in shows] if shows else []
            self.del_show_drop.options = [ft.DropdownOption(key=t, text=t) for t in show_titles]
            if not self.del_show_drop.value or self.del_show_drop.value not in show_titles:
                self.del_show_drop.value = show_titles[0] if show_titles else None
        else:
            self.del_show_drop.options = []
            self.del_show_drop.value = None

    def _on_del_uni_change(self, e):
        if e: e.control.value = e.data
        self._load_del_drops()
        self.update()

    def _show_confirm_dialog(self, content_text, confirm_callback):
        self.confirm_dialog_content.value = content_text
        self.confirm_callback_holder.clear()
        self.confirm_callback_holder.append(confirm_callback)
        self.confirm_overlay.visible = True
        self.update()

    def _close_confirm_dlg(self, e):
        self.confirm_overlay.visible = False
        self.update()

    def _execute_confirm(self, e):
        self.confirm_overlay.visible = False
        if self.confirm_callback_holder:
            self.confirm_callback_holder[0]()
        self.update()

    def _delete_show_action(self, e):
        if self.del_uni_drop.value and self.del_show_drop.value:
            def do_delete():
                self.state.db.delete_show(self.del_uni_drop.value, self.del_show_drop.value)
                self.state.refresh_data()
                self._load_del_drops()
            self._show_confirm_dialog(f"{self.state.t('are_you_sure_delete')} '{self.del_show_drop.value}'?", do_delete)

    def _delete_uni_action(self, e):
        if self.del_uni_drop.value:
            def do_delete():
                self.state.db.delete_universe(self.del_uni_drop.value)
                self.state.refresh_data()
                self._load_del_drops()
            self._show_confirm_dialog(f"{self.state.t('are_you_sure_delete_uni')} '{self.state.t_uni(self.del_uni_drop.value)}'?", do_delete)

    def _add_uni_action(self, e):
        if self.new_uni_input.value:
            self.state.db.add_universe(self.new_uni_input.value)
            self.new_uni_input.value = ""
            self.state.refresh_data()
            self._load_del_drops()
            self.update()