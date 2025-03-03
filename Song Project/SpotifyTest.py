import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Replace these with your actual Spotify credentials
SPOTIPY_CLIENT_ID = 'ccb9a0a8f693413e8fc92d12b3ce7b0d'
SPOTIPY_CLIENT_SECRET = 'ac0943264e04454eb09287b31ffb2e37'

try:
    # Authenticate with Spotify
    auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                            client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Test fetching audio features for a track
    track_id = '6rqhFgbbKwnb9MLmUQDhG6'  # Example track ID
    features = sp.audio_features([track_id])

    if features[0] is not None:
        print("Audio Features:", features[0])
    else:
        print("No audio features found for the track.")

except Exception as e:
    print("An error occurred:", e)
