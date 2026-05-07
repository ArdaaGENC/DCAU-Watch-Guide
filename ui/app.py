import customtkinter as ctk
import requests
from PIL import Image
from io import BytesIO
from core.database import load_timeline, load_progress, save_progress
from core.api import fetch_show_details

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
ACCENT_COLOR = "#f5c518"
SUCCESS_COLOR = "#2ecc71"
ERROR_COLOR = "#e74c3c"
TITLE_FONT = ("Segoe UI", 20, "bold")
NORMAL_FONT = ("Segoe UI", 13)
SMALL_FONT = ("Segoe UI", 12, "italic")

timeline_db = load_timeline()
universes = list(timeline_db.keys())

window = ctk.CTk()
window.title("Universal Tracker")
window.geometry("550x700")
window.minsize(450, 650)

main_frame = ctk.CTkFrame(window, fg_color="transparent")
main_frame.pack(expand=True, fill="both", padx=40, pady=20)

def update_show_menu(selected_universe):
    show_in_universe = timeline_db.get(selected_universe, [])
    show_combobox.configure(values=show_in_universe)

    saved_progress = load_progress()
    last_watched = saved_progress.get(selected_universe, show_in_universe[0] if show_in_universe else "")
    show_combobox.set(last_watched)

    result_label.configure(text="")
    details_label.configure(text="")
    poster_label.configure(image=None, text="")

def find_next_show():
    selected_universe = universe_combobox.get()
    selected_show = show_combobox.get()

    universe_list = timeline_db.get(selected_universe, [])

    if selected_show in universe_list:
        current_index = universe_list.index(selected_show)

        if current_index + 1 < len(universe_list):
            next_show = universe_list[current_index + 1]
            result_label.configure(text=f"Next up: {next_show}", text_color=SUCCESS_COLOR)

            details = fetch_show_details(next_show)
            details_label.configure(text=details["text"], text_color="#aaaaaa")

            if details["image_url"]:
                img_response = requests.get(details["image_url"])
                img_data = Image.open(BytesIO(img_response.content))
                ctk_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(160, 230))
                poster_label.configure(image=ctk_image, text="")
                poster_label.image = ctk_image
            else:
                poster_label.configure(image=None, text="No Poster Found")
                poster_label.image = None
        else:
            result_label.configure(text="🎉 Congratulations! You have finished this list.", text_color=SUCCESS_COLOR)
            details_label.configure(text="")
            poster_label.configure(image=None, text="")

        save_progress(selected_universe, selected_show)   
    else:
        result_label.configure(text="Please select a valid show.", text_color=ERROR_COLOR)

title_label = ctk.CTkLabel(main_frame, text="🎬 Universal Tracker", font=TITLE_FONT, text_color=ACCENT_COLOR)
title_label.pack(pady=(0, 20))

universe_label = ctk.CTkLabel(main_frame, text="Select Universe:", font=NORMAL_FONT)
universe_label.pack(pady=(0, 5))
universe_combobox = ctk.CTkComboBox(main_frame, values=universes, font=NORMAL_FONT, dropdown_font=NORMAL_FONT, border_color=ACCENT_COLOR, command=update_show_menu)
universe_combobox.pack(pady=(0, 15), fill="x")

show_label = ctk.CTkLabel(main_frame, text="Select Last Watched Show:", font=NORMAL_FONT)
show_label.pack(pady=(0, 5))
show_combobox = ctk.CTkComboBox(main_frame, values=[], font=NORMAL_FONT, dropdown_font=NORMAL_FONT, border_color=ACCENT_COLOR)
show_combobox.pack(pady=(0, 15), fill="x")

calculate_btn = ctk.CTkButton(main_frame, text="FIND NEXT SHOW", command=find_next_show, fg_color=ACCENT_COLOR, text_color="black", hover_color="#d4aa00", font=("Segoe UI", 14, "bold"), corner_radius=8, height=40)
calculate_btn.pack(pady=10, fill="x")

result_label = ctk.CTkLabel(main_frame, text="", font=("Segoe UI", 16, "bold"), wraplength=400)
result_label.pack(pady=10)
details_label = ctk.CTkLabel(main_frame, text="", font=SMALL_FONT)
details_label.pack(pady=5)
poster_label = ctk.CTkLabel(main_frame, text="")
poster_label.pack(pady=10)

def run():
    if universes:
        universe_combobox.set(universes[0])
        update_show_menu(universes[0])
    window.mainloop()