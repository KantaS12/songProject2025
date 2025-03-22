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
token_url = "https://api.genius.com/oauth/token"
payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'client_credentials'
}

response = requests.post(token_url, data=payload)
if response.status_code == 200:
    access_token = response.json().get('access_token')
else:
    exit(1)
"""
Our SQL database to add our information inside! We will be PostGreSQL 
because it seems like the easier one to use for our Query. 
"""
conn = psycopg2.connect(
    dbname="music_data",
    user="postgres",
    password="password",
    host="localhost"
)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS SONG )
               id SERIAL PRIMARY KEY,
               title VARCHAR(255),
               artist VARCHAR(255),
               album VARCHAR(255),
               lyrics TEXT,
               youtube_views BIGINT
    );
""")

cursor.execute("""
    INSERT INTO songs (title, artist, album, lyrics, youtube_views)
    VALUES (%s, %s, %s, %s, %s)
"""), 

conn.commit()

cursor.execute("SELECT * FROM songs")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()


