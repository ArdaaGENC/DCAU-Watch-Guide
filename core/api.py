import requests
import os
from dotenv import load_dotenv

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def fetch_show_details(show_name):
    is_movie = "(Film)" in show_name
    clean_name = show_name.replace(" (Film)", "")
    
    if is_movie:
        return fetch_from_omdb(clean_name)
    
    tvmaze_url = f"https://api.tvmaze.com/singlesearch/shows?q={clean_name}"
    
    try:
        response = requests.get(tvmaze_url)
        if response.status_code == 200:
            data = response.json()
            return format_tvmaze_data(data)
        
        return fetch_from_omdb(clean_name)
        
    except Exception as e:
        return {"text": "No Internet Connection", "image_url": None}

def fetch_from_omdb(show_name):
    if not OMDB_API_KEY:
        return {"text": "OMDb API key not configured", "image_url": None}
    omdb_url = f"http://www.omdbapi.com/?t={show_name}&apikey={OMDB_API_KEY}"

    try:
            res = requests.get(omdb_url)
            data = res.json()
            if data.get("Response") == "True":
                 rating = data.get("imdbRating", "N/A")
                 year = data.get("Year", "N/A")
                 poster = data.get("Poster", None)
                 poster_url = poster if poster != "N/A" else None

                 return{
                    "text": f"Rating: {rating}/10 | Year: {year} (Movie)",
                    "image_url": poster_url
                 }
    except:
        pass
    return {"text": "Show not found", "image_url": None}

def format_tvmaze_data(data):
     rating = data.get("rating", {}).get("average", "N/A")
     premiered = data.get("premiered", "N/A")
     image_url = data["image"].get("medium") if data.get("image") else None
     return {
        "text": f"Rating: {rating}/10 | Premiered: {premiered}",
        "image_url": image_url
     }