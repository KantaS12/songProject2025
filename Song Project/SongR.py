import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import requests
import os
import lyricsgenius as genius
import tkinter as tk
from tkinter import messagebox
load_dotenv()

client_id = os.getenv("GENIUS_CLIENT_ID")
client_secret = os.getenv("GENIUS_CLIENT_SECRET")

token_url = "https://api.genius.com/oauth/token"
payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'client_credentials'
}

response = requests.post(token_url, data=payload)
if response.status_code == 200:
    token_data = response.json()
    access_token = token_data.get('access_token')
    print("Access token retrieved successfully.")
else:
    print(f"Failed to retrieve token: {response.status_code} - {response.text}")
    exit(1)


def fetch_song():
    song_name = entry.get()

    search_url = "https://api.genius.com/search"

    params = {
        'q': song_name
    }

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        first_result = data['response']['hits'][0]['result']['title']
        messagebox.showinfo("Result", f"Found Song: {first_result}")
    else:
        messagebox.showerror("Error", f"Request failed: {response.status_code}")

root = tk.Tk()
root.title("Genius API Search")

entry = tk.Entry(root, width=50)
entry.pack(pady=10)

button = tk.Button(root, text="Search Song", command=fetch_song)
button.pack(pady=10)

root.mainloop()