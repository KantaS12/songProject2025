import os
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build
import tkinter as tk
from tkinter import messagebox

# Load environment variables
load_dotenv()
client_id = os.getenv("GENIUS_CLIENT_ID")
client_secret = os.getenv("GENIUS_CLIENT_SECRET")
youtube_api_key = os.getenv("YT_API_KEY")

# Obtain Genius access token
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

# Authenticate YouTube API using API key
youtube = build('youtube', 'v3', developerKey=youtube_api_key)

# Fetch YouTube video data
def fetch_youtube_video(query):
    request = youtube.search().list(part='snippet', q=query, maxResults=5, type='video')
    response = request.execute()
    videos = [(item['snippet']['title'], item['id']['videoId']) for item in response['items']]
    return videos

# Fetch song from Genius and YouTube
def fetch_song():
    song_name = entry.get().strip()
    if not song_name:
        messagebox.showwarning("Input Error", "Please enter a song name.")
        return

    # Search Genius API for the song
    search_url = "https://api.genius.com/search"
    params = {'q': song_name}
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if not data['response']['hits']:
            messagebox.showinfo("Result", "No songs found on Genius.")
            return

        first_result = data['response']['hits'][0]['result']
        title = first_result['title']
        artist = first_result['primary_artist']['name']
        videos = fetch_youtube_video(f"{title} {artist}")

        if videos:
            video_info = "\n".join([f"{i+1}. {video[0]}" for i, video in enumerate(videos)])
            messagebox.showinfo("YouTube Results", f"Found videos for '{title}' by {artist}:\n{video_info}")
        else:
            messagebox.showinfo("YouTube Results", "No videos found on YouTube.")
    else:
        messagebox.showerror("Error", f"Request failed: {response.status_code}")

# Tkinter GUI
root = tk.Tk()
root.title("Song Search App")

tk.Label(root, text="Enter a song name:").pack(pady=5)
entry = tk.Entry(root, width=50)
entry.pack(pady=10)

button = tk.Button(root, text="Search Song", command=fetch_song)
button.pack(pady=10)

root.mainloop()