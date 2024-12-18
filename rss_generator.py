import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

class SpotifyPodcastRSS:
    def __init__(self, client_id, client_secret):
        self.spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )

if __name__ == "__main__":
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    print("client_id", client_id)
    print("client_secret", client_secret)
    client = SpotifyPodcastRSS(client_id, client_secret)
    client.spotify
    urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'

    artist = client.spotify.artist(urn)

    if artist:
        template_path = os.path.join(os.path.dirname(__file__), 'subscribe.html')
        with open(template_path) as f:
            template = f.read()

        html_content = template.format(
            artist_name = artist['name']
        )

        print(artist)

        output_dir = "dist"

        os.makedirs(output_dir, exist_ok=True)

        index_path = os.path.join(os.path.dirname(__file__), output_dir, 'index.html')
        with open(index_path, 'w') as f:
            f.write(html_content)
