import flet as ft
import threading
from core.database import load_timeline
from core.api import fetch_show_details

def create_library_tab(page, switch_func):
    db = load_timeline()
    grid = ft.GridView(expand=True, max_extent=160, child_aspect_ratio=0.6, spacing=15)

    def load_posters(show, img_obj):
        det = fetch_show_details(show)
        if det and det.get("image_url"):
            img_obj.src = det.get("image_url")
            img_obj.visible = True
            try:
                if img_obj.page:
                    img_obj.update()
            except Exception:
                pass

    def build_grid(uni, is_initial=False):
        new_cards = []
        pending_downloads = []
        
        for show in db.get(uni, []):
            img = ft.Image(src="", visible=False, fit="contain")
            card = ft.Container(
                content=ft.Column([
                    ft.Container(img, width=120, height=180, bgcolor="#333333", border_radius=10),
                    ft.Text(
                        show, 
                        weight="bold", 
                        text_align="center",
                        size=13,
                        max_lines=2, 
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ], horizontal_alignment="center"),
                on_click=lambda e, s=show: switch_func(0, s)
            )
            new_cards.append(card)
            pending_downloads.append((show, img))
            
        grid.controls = new_cards
        
        if not is_initial and grid.page:
            try:
                grid.update()
            except Exception:
                pass
                
        for show, img in pending_downloads:
            threading.Thread(target=load_posters, args=(show, img), daemon=True).start()

    universes = list(db.keys())
    initial_uni = universes[0] if universes else None

    uni_drop = ft.Dropdown(
        options=[ft.DropdownOption(key=u, text=u) for u in universes],
        value=initial_uni, 
        width=300,
        on_select=lambda e: build_grid(e.control.value, is_initial=False)
    )
    
    if initial_uni:
        build_grid(initial_uni, is_initial=True)

    return ft.Container(
        content=ft.Column([uni_drop, grid], horizontal_alignment="center"),
        expand=True,
        padding=20
    )