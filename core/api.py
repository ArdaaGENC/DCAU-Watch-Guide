import requests
import os
import json
import re
from dotenv import load_dotenv

class APIClient:
    def __init__(self, db_manager):
        load_dotenv()
        self._omdb_api_key = os.getenv("OMDB_API_KEY")
        self._db_manager = db_manager
        
        self._cache = {}
        self._cache_file = os.path.join("data", "api_cache.json")
        self._posters_dir = os.path.join("data", "posters")
        
        os.makedirs(self._posters_dir, exist_ok=True)
        self._persistent_cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self._cache_file):
            try:
                with open(self._cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {}

    def _save_cache(self):
        with open(self._cache_file, "w", encoding="utf-8") as f:
            json.dump(self._persistent_cache, f, indent=4)

    def _get_show_metadata(self, show_name):
        db = self._db_manager.load_timeline()
        for universe, shows in db.items():
            for item in shows:
                if isinstance(item, dict) and item.get("title") == show_name:
                    return item.get("type", "show"), item.get("release", "")
                elif isinstance(item, str):
                    clean_str = item.replace(" (Film)", "")
                    if clean_str == show_name or item == show_name:
                        return "movie" if "(Film)" in item else "show", ""
        return "show", ""

    def fetch_show_details(self, show_name):
        if show_name in self._cache:
            return self._cache[show_name]

        if show_name in self._persistent_cache:
            self._cache[show_name] = self._persistent_cache[show_name]
            return self._cache[show_name]

        clean_name = show_name.replace(" (Film)", "")
        show_type, release_year = self._get_show_metadata(clean_name)
        is_movie = (show_type == "movie")
        
        result = None
        
        if release_year or is_movie:
            omdb_type = "movie" if is_movie else "series"
            result = self._fetch_from_omdb(clean_name, release_year, omdb_type)
            
        if is_movie:
            if not result: result = {"text": "Movie not found", "image_url": None}
        else:
            if not result or not result.get("image_url"):
                tvmaze_url = f"https://api.tvmaze.com/singlesearch/shows?q={clean_name}"
                try:
                    response = requests.get(tvmaze_url)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("image"):
                            result = self._format_tvmaze_data(data)
                except: pass
            if not result:
                result = self._fetch_from_omdb(clean_name, "", "series")
                
        if not result:
            result = {"text": "Show not found", "image_url": None}

        if result.get("image_url"):
            safe_name = re.sub(r'[\\/*?:"<>|]', "", clean_name)
            local_path = os.path.abspath(os.path.join(self._posters_dir, f"{safe_name}.jpg"))
            
            try:
                img_data = requests.get(result["image_url"]).content
                with open(local_path, 'wb') as handler:
                    handler.write(img_data)
                result["local_image_path"] = local_path
            except:
                result["local_image_path"] = None
        else:
            result["local_image_path"] = None

        self._cache[show_name] = result
        self._persistent_cache[show_name] = result
        self._save_cache()
        
        return result

    def _fetch_from_omdb(self, show_name, year="", type_filter=""):
        if not self._omdb_api_key: return None
        omdb_url = f"http://www.omdbapi.com/?t={show_name}&apikey={self._omdb_api_key}"
        if year: omdb_url += f"&y={year}"
        if type_filter: omdb_url += f"&type={type_filter}"
        try:
            res = requests.get(omdb_url)
            data = res.json()
            if data.get("Response") == "True":
                 return {
                    "text": f"Rating: {data.get('imdbRating', 'N/A')}/10 | Year: {data.get('Year', 'N/A')} ({'Movie' if type_filter == 'movie' else 'Show'})",
                    "image_url": data.get("Poster") if data.get("Poster") != "N/A" else None
                 }
        except: pass
        return None

    def _format_tvmaze_data(self, data):
         premiered = data.get("premiered", "N/A")
         year = premiered.split("-")[0] if premiered and premiered != "N/A" else "N/A"
         return {
            "text": f"Rating: {data.get('rating', {}).get('average', 'N/A')}/10 | Year: {year} (Show)",
            "image_url": data["image"].get("medium") if data.get("image") else None
         }