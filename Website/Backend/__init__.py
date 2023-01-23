from .secret import Secrets
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

secrets = Secrets()

client_id = secrets["spotifyClientID"]
client_secret = secrets["spotifyClientSecret"]

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))