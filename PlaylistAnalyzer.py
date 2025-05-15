from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import csv
from collections import Counter

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
    
    def get_artist_id(self, token, id):
        url = f"https://api.spotify.com/v1/tracks/{id}?country=UA"
        headers = super().get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        artists = []
        for artist in json_result["artists"]:
            artist_id = artist["id"]
            artists.append(artist_id)
        return(artists)

class ArtistAnalyzer(OAuth_2):
    def get_artist_name(self, token, id):
        url = f"https://api.spotify.com/v1/artists/{id}"
        headers = super().get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        return json_result["name"]

    def get_artist_genres(self, token, id):
        url = f"https://api.spotify.com/v1/artists/{id}"
        headers = super().get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        return json_result["genres"]
        
class PlaylistAnalyzer(OAuth_2):
    def using_tracks_id(self, token, playlist_id, file):
        offset = 0
        limit = 100

        with open(file, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Track name", "Album name", "Release date", "Popularity", "Duration", "Artist name", "Genres"])
            writer.writeheader()

        while True:
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?country=UA&offset={offset}&limit={limit}"
            headers = super().get_auth_header(token)
            result = get(url, headers=headers)
            json_result = json.loads(result.content)
            for item in json_result["items"]:
                if item.get("track"):
                    track_id = TrackAnalyzer()
                    track_name = track_id.get_track_name(token, item["track"]["id"])
                    album_name = track_id.get_album_name(token, item["track"]["id"])
                    album_release_date = track_id.get_album_release_date(token, item["track"]["id"])
                    track_popularity = track_id.get_track_popularity(token, item["track"]["id"])
                    track_duration = track_id.get_track_duration(token, item["track"]["id"])
                    minutes = (track_duration/1000) // 60
                    seconds = (track_duration/1000) % 60
                    final_time = f"{int(minutes)}:{int(seconds):02}"
                    artist_ids = track_id.get_artist_id(token, item["track"]["id"])
                    artist_info = ArtistAnalyzer()
                    names = []
                    genre_set = set()
                    for artist_id in artist_ids:
                        names.append(artist_info.get_artist_name(token, artist_id))
                        genre_set.update(artist_info.get_artist_genres(token, artist_id))
                    artist_name = ", ".join(names)
                    artist_genre = ", ".join(sorted(genre_set))

                    with open(file, "a", encoding="utf-8", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=["Track name", "Album name", "Release date", "Popularity", "Duration", "Artist name", "Genres"])
                        writer.writerow({"Track name": track_name, "Album name": album_name, "Release date": album_release_date, "Popularity": track_popularity, "Duration": final_time, "Artist name": artist_name, "Genres": artist_genre})
            if len(json_result["items"]) < limit:
                break
            offset += limit
        
    def count_num_of_tracks(self, file):
        with open(file, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            return sum(1 for _ in reader)
        
    def count_num_of_artist(self, file):
        counts = Counter()
        with open(file, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                artists = [name.strip() for name in row['Artist name'].split(',')]
                for artist in artists:
                    counts[artist] += 1 
        return counts
    
    def count_num_of_length(self, file):
        counts = Counter()
        with open(file, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                minutes = row['Duration'].split(':')[0]
                counts[minutes] += 1 
        return counts
    
    def count_num_of_decade(self, file):
        counts = Counter()
        with open(file, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                decades = int(row['Release date'].split('-')[0]) // 10 * 10
                counts[decades] += 1 
        return counts

    def count_num_of_genres(self, file):
        counts = Counter()
        with open(file, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                genres = [name.strip() for name in row['Genres'].split(',')]
                for genre in genres:
                    counts[genre] += 1 
        return counts

def main():
    playlist_url = "https://open.spotify.com/playlist/5dTk7jitcBaDbNuvxqWu7M?si=c9ee7d78559f40ac"
    playlist_id = playlist_url.split("/playlist/")[1].split("?")[0]

    file = "all_info.csv"
    open("all_info.csv", "w", encoding="utf-8", newline="")

    authorization = OAuth_2()
    token = authorization.get_token()

    playlist = PlaylistAnalyzer()
    playlist.using_tracks_id(token, playlist_id, file)
    total_tracks = playlist.count_num_of_tracks(file)
    print(f"Total num of tracks - {total_tracks}")
    total_artists = playlist.count_num_of_artist(file)
    all_artists = ", ".join([f"'{key}': {value}" for key, value in total_artists.most_common(10)])
    print(f"Most common artists - {all_artists}")
    total_lengths = playlist.count_num_of_length(file)
    all_lengths = ", ".join([f"'{key}-{int(key)+1} min': {value}" for key, value in total_lengths.items()])
    print(f"Most common lengths - {all_lengths}")
    total_decades = playlist.count_num_of_decade(file)
    all_decades = ", ".join([f"'{key}s': {value}" for key, value in total_decades.items()])
    print(f"Most common decade - {all_decades}")
    total_genres = playlist.count_num_of_genres(file)
    all_genres = ", ".join([f"'{key}': {value}" for key, value in total_genres.most_common(5)])
    print(f"Most common artists - {all_genres}")
    
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

# Analyze playlist (id tracks) -> Analyze track (name, album, release date, popularity, duration, id artist) -> Analyze Artist(name, genres)
# Counters (num of tracks, amount of times per artist, length, decade of release, genre)

# Display all table with sorted(Track name,Album name,Release date,Popularity,Duration,Artist name,Genres), display decade, duration, artist, genre that i want

# Create graphs