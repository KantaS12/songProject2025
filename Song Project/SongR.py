import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                           client_secret=SPOTIPY_CLIENT_SECRET))

# Step 2: Fetch song features from Spotify
def get_song_features(track_id):
    """
    Fetch audio features for a given track ID from Spotify.
    """
    features = sp.audio_features([track_id])[0]
    return {
        'danceability': features['danceability'],
        'energy': features['energy'],
        'key': features['key'],
        'loudness': features['loudness'],
        'mode': features['mode'],
        'speechiness': features['speechiness'],
        'acousticness': features['acousticness'],
        'instrumentalness': features['instrumentalness'],
        'liveness': features['liveness'],
        'valence': features['valence'],
        'tempo': features['tempo']
    }

# Step 3: Normalize the features
def normalize_features(features_df):
    """
    Normalize the song features using MinMaxScaler.
    """
    scaler = MinMaxScaler()
    normalized_features = scaler.fit_transform(features_df)
    return pd.DataFrame(normalized_features, columns=features_df.columns)

# Step 4: Find similar songs
def find_similar_songs(input_track_id, all_tracks_features, top_n=5):
    """
    Find the most similar songs based on cosine similarity.
    """
    # Get features of the input track
    input_features = pd.DataFrame([get_song_features(input_track_id)])
    
    # Normalize all features including the input track
    all_features_normalized = normalize_features(pd.concat([all_tracks_features, input_features]))
    
    # Separate the input track features
    input_track_normalized = all_features_normalized.iloc[-1].values.reshape(1, -1)
    all_features_normalized = all_features_normalized.iloc[:-1]
    
    # Compute cosine similarity
    similarities = cosine_similarity(input_track_normalized, all_features_normalized)
    
    # Get top N similar tracks
    similar_indices = np.argsort(similarities[0])[::-1][:top_n]
    return similar_indices

# Step 5: Main function to recommend songs
def recommend_songs(input_track_id, all_tracks_ids, top_n=5):
    """
    Recommend similar songs based on the input track.
    """
    # Fetch features for all tracks
    all_tracks_features = []
    for track_id in all_tracks_ids:
        all_tracks_features.append(get_song_features(track_id))
    
    all_tracks_features = pd.DataFrame(all_tracks_features)
    
    # Find similar songs
    similar_indices = find_similar_songs(input_track_id, all_tracks_features, top_n)
    
    # Return the recommended track IDs
    recommended_track_ids = [all_tracks_ids[i] for i in similar_indices]
    return recommended_track_ids

# Example usage
if __name__ == "__main__":
    # Example track IDs (you can replace these with actual Spotify track IDs)
    input_track_id = '6rqhFgbbKwnb9MLmUQDhG6'  # Example track ID
    all_tracks_ids = ['6rqhFgbbKwnb9MLmUQDhG6', '7dGJo4pcD2V6oG8kP0tJRR', '51Blml2LZPmy7TTiAg47vQ']

    # Get recommendations
    recommended_tracks = recommend_songs(input_track_id, all_tracks_ids, top_n=3)
    print("Recommended Track IDs:", recommended_tracks)