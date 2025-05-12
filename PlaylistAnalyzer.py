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
    def get_track_name(self, token, playlist_id, id):
        url = f"https://api.spotify.com/v1/tracks/{id}?country=UA"
        headers = super().get_auth_header(token)

        result = get(url, headers=headers)
        json_result = json.loads(result.content)["name"]
        return(json_result)

        
class PlaylistAnalyzer(OAuth_2):
    # def total_num_of_tracks(self, token, playlist_id):
    #     url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?country=UA"
    #     headers = super().get_auth_header(token)

    #     result = get(url, headers=headers)
    #     json_result = json.loads(result.content)["total"]
    #     return(json_result)

    def get_tracks_id(self, token, playlist_id, file):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?country=UA"
        headers = super().get_auth_header(token)
        
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        
        for item in json_result["items"]:
            if item.get("track"):
                id = TrackAnalyzer()
                track_name = id.get_track_name(token, playlist_id, item["track"]["id"]) 
                with open(file, "w", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["track_name"])
                    writer.writerow({"track_name": track_name})

        return(track_name)
    
def main():
    playlist_url = "https://open.spotify.com/playlist/09O7iNrTUfjBynKemR9gkU?si=cc926f09d7f24006"
    playlist_id = playlist_url.split("/playlist/")[1].split("?")[0]

    file = "all_info.csv"

    authorization = OAuth_2()
    token = authorization.get_token()

    playlist = PlaylistAnalyzer()
    # total_songs = playlist.total_num_of_tracks(token, playlist_id)
    # print(f"Total number of tracks: {total_songs}")
    all_artists = playlist.get_tracks_id(token, playlist_id, file)
    print(f"all id's - {all_artists}")

if __name__ == "__main__":
    main()

# All required info
# =========================================
# 1. Total number of tracks
# 2. Total number of artists
# 3. Average song length + graph
# 4. Average BPM (Beats Per Minute) + graph ?
# 5. Decade of release
# 6. Popularity
# 7. Most common artist, genre, length + graph
# ==========================================

# Analyze playlist (id tracks, (added_at)) -> Analyze track (name, album, release date, popularity, id artist, duration) -> Analyze Artist(name, genres(parent genres/genres))