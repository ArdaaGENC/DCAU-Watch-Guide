# DCAU Watch Guide - Version 5.2 (Updated Timeline and Added TVmaze API Integration)
import tkinter as tk
from tkinter import ttk
import json
import os
import requests


def load_timeline():
    try:
        with open("timeline.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("HATA: timeline.json dosyası bulunamadı!")
        return {"hata": "Veritabanı Bulunamadı"}

dcau_timeline = load_timeline()

# Function to save the user's last watched show to a JSON file
def save_progress(last_show_name):
    data = {"last_watched": last_show_name}
    with open("progress.json", "w") as f:
        json.dump(data, f)

# Function to load the user's last watched show from a JSON file
def load_progress():
    if os.path.exists("progress.json"):
        with open("progress.json", "r") as f:
            data = json.load(f)
            return data.get("last_watched", "Select a series...")
    return "Select a series..."

# Fetches live data from TVmaze API
def fetch_show_details(show_name):
    api_url = f"https://api.tvmaze.com/singlesearch/shows?q={show_name}"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            rating = data["rating"]["average"]
            premiered = data["premiered"]
            return f"Rating: {rating}/10 | Premiered: {premiered}"
        else:
            return "Details not available"
    except:
        return "No internet connection"
    
# Function to find the next show based on the selected show
def find_next_show():
    selected_show = show_combobox.get()

    if selected_show in dcau_timeline:
        next_show = dcau_timeline[selected_show]
        save_progress(selected_show)
        result_label.config(text=f"Next up: {next_show}", fg="green")
        details = fetch_show_details(next_show)
        details_label.config(text=details, fg="blue")
    else:
        result_label.config(text="Please select a valid show from the list.", fg="red")
        details_label.config(text="")
# Create the main application window
window = tk.Tk()
window.title("DCAU Watch Guide")
window.geometry("450x250")
window.eval('tk::PlaceWindow . center')

# Title label
title_label = tk.Label(window, text="Welcome to the DCAU Watch Guide!", font=("Arial", 14, "bold"))
title_label.pack(pady=15)

# Instruction label
instruction_label = tk.Label(window, text="Which series did you finish last?", font=("Arial", 10))
instruction_label.pack(pady=5)

# Combobox
show_list = list(dcau_timeline.keys())
show_combobox = ttk.Combobox(window, values=show_list, width=35, state="readonly")
saved_show = load_progress()
show_combobox.set(saved_show)
show_combobox.pack(pady=5)

# Calculate button
calculate_btn = tk.Button(window, text="Find Next Show", command=find_next_show, bg="black", fg="white", font=("Arial", 10, "bold"))
calculate_btn.pack(pady=15)

# Result label
result_label = tk.Label(window, text="", font=("Arial", 12, "bold"))
result_label.pack(pady=5)

# Details label
details_label = tk.Label(window, text="", font=("Arial", 10, "italic"))
details_label.pack(pady=5)

window.mainloop()