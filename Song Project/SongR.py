import os
import requests
import psycopg2
from dotenv import load_dotenv
from googleapiclient.discovery import build

"""
Import the API's, we will be using GENIUS API and Youtube API 
for our analysis!
"""
load_dotenv()
client_id = os.getenv("GENIUS_CLIENT_ID")
client_secret = os.getenv("GENIUS_CLIENT_SECRET")
youtube_api_key = os.getenv("YT_API_KEY")

youtube = build('youtube', 'v3', developerKey=youtube_api_key)
def genius_access_token(): 
    token_url = "https://api.genius.com/oauth/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception("Failed to obtain Genius API token")
"""
Our SQL database to add our information inside! We will be PostGreSQL 
because it seems like the easier one to use for our Query. 
"""
conn = psycopg2.connect(
    dbname="music_data",
    user="kantasaito",
    password="",
    host="localhost"
)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS SONG (
               id SERIAL PRIMARY KEY,
               title VARCHAR(255),
               artist VARCHAR(255),
               album VARCHAR(255),
               lyrics TEXT,
               youtube_views BIGINT
    );
""")

"""
We're using the API for Genius to give us the song and we're getting
either an empty array or an array with the information if we get an ok
from HTTPS.
"""
def search_song(query, access_token):
    url = "https://api.genius.com/search"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, params={"q": query})
    if response.status_code == 200:
        return response.json()['response']['hits']
    return[]

"""
Same thing, we're using the API for Genius to give us our lyrics.
"""
def fetch_lyrics(song_id, access_token):
    url = f"https://api.genius.com/songs/{song_id}?text_format=plain"
    headers = {"Authroization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        print("Genius API Response:", data)
        if 'lyrics' in data['response']['song']:
            return data['response']['song']['lyrics']['plain']
        else:
            print(f"No lyrics field found for song ID: {song_id}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching lyrics from Genius API: {e}")
        return None

def get_youtube_views(query):
    url="https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q" : query,
        "type": "video",
        "key": youtube_api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        video_id = response.json()['items'][0]['id']['videoId']
        stats_url = "https://www.googleapis.com/youtube/v3/videos"
        stats_params = {
            "part": "statistics",
            "id": video_id,
            "key": youtube_api_key
        }
        stats_response = requests.get(stats_url, params=stats_params)
        if stats_response.status_code == 200:
            return int(stats_response.json()['items'][0]['statistics']['viewCount'])
        return None
    
def insert_song(title, artist, album, lyrics, youtube_views):
    cursor.execute("""
    INSERT INTO songs (title, artist, album, lyrics, youtube_views)
    VALUES (%s, %s, %s, %s, %s)
""", (title, artist, album, lyrics, youtube_views))
    conn.commit()

def process_songs(song_queries):
    access_token = genius_access_token()
    print("Genius API token granted")
    for query in song_queries:
        print(f"Processing: {query}")
        genius_result = search_song(query, access_token)
        if not genius_result:
            print(f"No results found for: {query}")
            continue
        song_info = genius_result[0]['result']
        title = song_info['title']
        artist = song_info['primary_artist']['name']
        album = song_info.get('album', {}).get('name', '')
        song_id = song_info['id']

        lyrics = fetch_lyrics(song_id, access_token)
        if not lyrics:
            print(f"No lyrics found for: {query}")
            continue
            
        youtube_views = get_youtube_views(query)
        if not youtube_views:
            print(f"No Youtube views found for: {query}")
            continue
        
        insert_song(title, artist, album, lyrics, youtube_views)
        print(f"Inserted: {title} by {artist}")

if __name__ == "__main__":
    song_queries = [
        "Beautiful Things Benson Boone",
        "I Had Some Help Post Malone",
        "Lovin on Me Jack Harlow",
        "Bohemian Rhapsody Queen"
    ]
    process_songs(song_queries)
    cursor.close()
    conn.close()


