import flet as ft
from core.database import load_timeline, load_progress, save_progress
from core.api import fetch_show_details

def create_tracker_tab(page, switch_func, auto_select_show=None):
    db = load_timeline()
    universes = list(db.keys())
    initial_uni = universes[0] if universes else None
    
    if auto_select_show:
        for u, shows in db.items():
            if auto_select_show in shows:
                initial_uni = u
                break

    initial_shows = db.get(initial_uni, [])
    progress = load_progress()
    initial_val = auto_select_show if auto_select_show else progress.get(initial_uni, initial_shows[0] if initial_shows else "")

    show_drop = ft.Dropdown(
        options=[ft.DropdownOption(key=s, text=s) for s in initial_shows], 
        value=initial_val, 
        width=300, 
        label="Show"
    )
    res_label = ft.Text("", size=18, weight="bold", color="green")
    poster = ft.Image(src="", width=160, height=230, fit="contain", visible=False)

    def on_uni_select(e):
        new_uni = e.control.value
        print(f"\n--- SİNYAL ULAŞTI (FLET 1.0) ---")
        print(f"Seçilen Evren: {new_uni}")
        
        u_shows = db.get(new_uni, [])
        show_drop.options.clear()
        
        for s in u_shows:
            show_drop.options.append(ft.DropdownOption(key=s, text=s))
            
        show_drop.value = progress.get(new_uni, u_shows[0] if u_shows else "")
        res_label.value = ""
        poster.visible = False
        
        e.page.update()

    uni_drop = ft.Dropdown(
        options=[ft.DropdownOption(key=u, text=u) for u in universes], 
        value=initial_uni, 
        width=300, 
        label="Universe",
        on_select=on_uni_select  
    )

    def find_next(e):
        u_list = db.get(uni_drop.value, [])
        if show_drop.value in u_list:
            idx = u_list.index(show_drop.value)
            if idx + 1 < len(u_list):
                nxt = u_list[idx + 1]
                res_label.value = f"Next: {nxt}"
                det = fetch_show_details(nxt)
                if det and det.get("image_url"):
                    poster.src = det.get("image_url")
                    poster.visible = True
            else:
                res_label.value = "🎉 List Finished!"
                poster.visible = False
            
            save_progress(uni_drop.value, show_drop.value)
            e.page.update()

    return ft.Container(
        content=ft.Column([
            uni_drop, show_drop,
            ft.ElevatedButton("FIND NEXT", bgcolor="amber", color="black", on_click=find_next, width=300),
            res_label, poster
        ], horizontal_alignment="center", spacing=20),
        alignment=ft.Alignment(0, 0),
        padding=40
    )