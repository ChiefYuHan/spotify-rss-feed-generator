import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from feedgen.feed import FeedGenerator
import datetime


load_dotenv()

class SpotifyPodcastRSS:
    def __init__(self, client_id, client_secret):
        self.spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )

    def get_show_episodes(self, show_id):
        """Get all episodes from a show"""
        results = self.spotify.show_episodes(show_id)
        if results is None:
            return []

        episodes = results['items']

        while results['next']:
            next_results = self.spotify.next(results)
            if next_results is None:
                break
            results = next_results
            episodes.extend(results['items'])

        return episodes

    def generate_rss_feed(self, show_id, output_dir="dist"):
        os.makedirs(output_dir, exist_ok=True)

        show = self.spotify.show(show_id)

        if not show:
            raise ValueError(f"Show {show_id} not found")

        fg = FeedGenerator()
        fg.title(show['name']) # name of show
        fg.description(show['description']) # description of show
        fg.link(href=show['external_urls']['spotify']) # spotify url to show
        fg.language(show['languages'][0]) # language of show
        fg.image(show['images'][0]['url']) # cover image of show

        # Add episodes
        episodes = self.get_show_episodes(show_id)
        for episode in episodes:
            fe = fg.add_entry()
            fe.title(episode['name'])
            fe.description(episode['description'])
            fe.link(href=episode['external_urls']['spotify'])
            fe.published(datetime.datetime.strptime(
                episode['release_date'], '%Y-%m-%d'
            ).strftime('%a, %d %b %Y %H:%M:%S +0000'))

        feed_path = os.path.join(output_dir, 'feed.xml')
        fg.rss_file(feed_path)

        template_path = os.path.join(os.path.dirname(__file__), 'subscribe.html')
        episode_template_path = os.path.join(os.path.dirname(__file__), 'episode_template.html')
        with open(template_path) as f:
            template = f.read()

        with open(episode_template_path) as f:
            episode_template = f.read()

        # Build all episodes HTML
        episodes_html = []
        for episode in episodes:
            # Format the date
            date = datetime.datetime.strptime(episode['release_date'], '%Y-%m-%d')
            formatted_date = date.strftime('%B %d, %Y')

            # Format each episode
            episode_html = episode_template.format(
                episode_title=episode['name'],
                episode_date=formatted_date,
                episode_description=episode['description'],
                episode_spotify_url=episode['external_urls']['spotify']
            )
            episodes_html.append(episode_html)

        all_episodes = '\n'.join(episodes_html)

        html_content = template.format(
            show_name = show['name'],
            show_description = show['description'],
            cover_image = show['images'][0]['url'],
            spotify_url = show['external_urls']['spotify'],
            episodes=all_episodes
        )

        index_path = os.path.join(os.path.dirname(__file__), output_dir, 'index.html')
        with open(index_path, 'w') as f:
            f.write(html_content)

if __name__ == "__main__":
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    client = SpotifyPodcastRSS(client_id, client_secret)

    show_id = "6haxSH3TMIrt4BSFicMUgK"
    rss_gen = SpotifyPodcastRSS(client_id, client_secret)
    rss_gen.generate_rss_feed(show_id)
