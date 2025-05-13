from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import csv

load_dotenv()
client_id = os.getenv("CLIENT_ID") 
client_secret = os.getenv("CLIENT_SECRET")

class OAuth_2:
    def get_token(self):
        auth_string = client_id + ":" + client_secret                   # Створення авторизаційної строки необхідної для отримання токену доступу
        auth_bytes = auth_string.encode("utf-8")                        # Перетворює строку в байти, що потрібно для кодування в Base64
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")        # Кодує байти в Base64 та знову перетворює результат у строку яку можна використоти у заголовку авторизації

        url = "https://accounts.spotify.com/api/token"                  # Відправлення запиту за цією адресою для отримання токену
        headers = {
            "Authorization": "Basic " + auth_base64,                    # Ідентифікація клієнта який надсилає запит
            "Content-Type": "application/x-www-form-urlencoded"         # Вказується формат даних у POST-запиті
        }
        data = {"grant_type": "client_credentials"}                     # Готує дані для POST-запиту
        result = post(url, headers=headers, data=data)                  # HTTP POST-запит до url
        json_result = json.loads(result.content)                        # Перетворює JSON-відповідь сервера у словник Python.
        token = json_result["access_token"]                             # Витягує з словника токен доступу
        return token

    def get_auth_header(self, token):
        return {"Authorization": "Bearer " + token}                     # Створення заголовку який необхідний для надсилання API-запитів, щоб сервер знав, що ти авторизований

class TrackAnalyzer(OAuth_2):
    def get_track_name(self, token, id):
        url = f"https://api.spotify.com/v1/tracks/{id}?country=UA"
        headers = super().get_auth_header(token)

        result = get(url, headers=headers)
        json_result = json.loads(result.content)["name"]
        return(json_result)
    def get_album_name(self, token, id):
        url = f"https://api.spotify.com/v1/tracks/{id}?country=UA"
        headers = super().get_auth_header(token)

        result = get(url, headers=headers)
        json_result = json.loads(result.content)["album"]["name"]
        return(json_result)
    def get_album_release_date(self, token, id):
        url = f"https://api.spotify.com/v1/tracks/{id}?country=UA"
        headers = super().get_auth_header(token)

        result = get(url, headers=headers)
        json_result = json.loads(result.content)["album"]["release_date"]
        return(json_result)
    def get_track_popularity(self, token, id):
        url = f"https://api.spotify.com/v1/tracks/{id}?country=UA"
        headers = super().get_auth_header(token)

        result = get(url, headers=headers)
        json_result = json.loads(result.content)["popularity"]
        return(json_result)
    def get_track_duration(self, token, id):
        url = f"https://api.spotify.com/v1/tracks/{id}?country=UA"
        headers = super().get_auth_header(token)

        result = get(url, headers=headers)
        json_result = json.loads(result.content)["duration_ms"]
        return(json_result)

        
class PlaylistAnalyzer(OAuth_2):
    def using_tracks_id(self, token, playlist_id, file):
        offset = 0
        limit = 100

        with open(file, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Track name", "Album name", "Release date", "Popularity", "Duration"])
            writer.writeheader()

        while True:
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?country=UA&offset={offset}&limit={limit}"
            headers = super().get_auth_header(token)
            
            result = get(url, headers=headers)
            json_result = json.loads(result.content)
            for item in json_result["items"]:
                if item.get("track"):
                    id = TrackAnalyzer()
                    track_name = id.get_track_name(token, item["track"]["id"])
                    album_name = id.get_album_name(token, item["track"]["id"])
                    album_release_date = id.get_album_release_date(token, item["track"]["id"])
                    track_popularity = id.get_track_popularity(token, item["track"]["id"])
                    track_duration = id.get_track_duration(token, item["track"]["id"])
                    minutes = (track_duration/1000) // 60
                    seconds = (track_duration/1000) % 60
                    final_time = f"{int(minutes)}:{int(seconds):02}"
                    with open(file, "a", encoding="utf-8", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=["Track name", "Album name", "Release date", "Popularity", "Duration"])
                        writer.writerow({"Track name": track_name, "Album name": album_name, "Release date": album_release_date, "Popularity": track_popularity, "Duration": final_time})
            if len(json_result["items"]) < limit:
                break
            offset += limit
        
        return()
    
def main():
    playlist_url = "https://open.spotify.com/playlist/09O7iNrTUfjBynKemR9gkU?si=cc926f09d7f24006"
    playlist_id = playlist_url.split("/playlist/")[1].split("?")[0]

    file = "all_info.csv"

    authorization = OAuth_2()
    token = authorization.get_token()

    playlist = PlaylistAnalyzer()
    all_artists = playlist.using_tracks_id(token, playlist_id, file)
    print(f"all id's - {all_artists}")

if __name__ == "__main__":
    main()

# All required info
# =========================================
# 1. Total number of tracks
# 2. Total number of artists
# 3. Average song length + graph
# 4. Decade of release
# 5. Popularity
# 6. Most common artist, genre, length + graph
# ==========================================

# Analyze playlist (id tracks) -> Analyze track (name, album, release date, popularity, duration, id artist) -> Analyze Artist(name, genres(parent genres/genres))