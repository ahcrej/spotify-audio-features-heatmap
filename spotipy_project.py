import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from dotenv import load_dotenv
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

# Load the following environment variables from .env file:
# (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)
load_dotenv()

# Authentication
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


def remap(oldValue, oldMin, oldMax, newMin, newMax):
    # Remaps a value between an old range, to a value within a new range whilst maintaing the same ratio
    oldRange = (oldMax - oldMin)
    newRange = (newMax - newMin)
    newValue = (((oldValue - oldMin) * newRange) / oldRange) + newMin

    return newValue


def get_top_five_dict(artist_URL):
    # Returns a dictionary of an artist's Top 5 tracks and associated URIs
    artist_URI = artist_URL.split("/")[-1]
    results = sp.artist_top_tracks(artist_URI)
    d = {track["name"]: track["uri"] for track in results['tracks'][:5]}

    return d


def get_album_dict(album_URL):
    # Returns a dictionary of an album's tracks and associated URIs
    album_URI = album_URL.split("/")[-1]
    results = sp.album_tracks(album_URI)
    d = {track["name"]: track["uri"] for track in results["items"]}

    return d


def get_album_name(album_URL):
    # Returns the name of an album based on the album URL
    album_URI = album_URL.split("/")[-1]
    album_name = sp.album(album_URI)["name"]
    
    return album_name


def get_audio_features(track_dict):
    # Returns a dictionary of dictionaries {"track_name": {audio_features}}
    d = {}

    # Create a list of track URIs when given a dictionary of tracks {"track_name": "uri"}
    track_list = [value for value in track_dict.values()]

    for track in sp.audio_features(track_list):
        track_URI = track["uri"]
        # The track() function returns information about a track in JSON format
        # To access the name: sp.track(track_URI)["name"]
        track_name = sp.track(track_URI)["name"]

        # Copy the audio features dictionary for a track
        track_copy = track.copy()
        # Remove unwanted key-value pairs that are returned by sp.audio_features()
        [track_copy.pop(x) for x in ["mode", "key", "type", "id", "track_href",
                                     "analysis_url", "uri", "duration_ms", "time_signature", "tempo"]]

        # Remap the loudness to a value within 0 and 1 (previously -60 to 0 dB)
        track_copy["loudness"] = round(
            remap(track_copy["loudness"], -60, 0, 0, 1), 3)

        # Add key-value (track name: track audio features) to the dictionary of dictionaries
        d[track_name] = track_copy

    return d


def main():
    # Set the link of the album to be analysed
    album_URL = "https://open.spotify.com/album/3HLwiAL4LbHVwQaVCl3tnR"

    # Get the audio features of each song of an album
    album_dict = get_album_dict(album_URL)
    album_features = get_audio_features(album_dict)

    # Convert the dictionary to a DataFrame for Seaborn
    df = pd.DataFrame(album_features)

    # Create a heatmap using Seaborn
    # Set the figure size
    plt.figure(figsize=(16, 6))
    # 'annot' for displaying values, 'cmap' for color map, 'fmt' for format of annotations
    sns.heatmap(df, annot=True, cmap='YlGnBu', fmt='.2f')

    # Customize the plot (optional)
    plot_title = get_album_name(album_URL)
    plt.title(plot_title)

    # Automatically adjust plot parameters so that the plot fits within the figrue area.
    plt.tight_layout()

    # Save the plot .png to the project folder
    plt.savefig(f"{plot_title} Heatmap.png", dpi=300)

    # Show the plot
    plt.show()


if __name__ == "__main__":
    main()