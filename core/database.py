import json
import os

TIMELINE_FILE = os.path.join("data", "timeline.json")
PROGRESS_FILE = os.path.join("data", "progress.json")

def load_timeline():
    try:
        with open(TIMELINE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"HATA: {TIMELINE_FILE} bulunamadı!")
        return {}

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_progress(universe_name, show_name):
    progress_data = load_progress()
    progress_data[universe_name] = show_name
    os.makedirs("data", exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=4)