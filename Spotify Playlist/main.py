# Musical Time Machine
import datetime as dt
import os
from pathlib import Path

import spotipy
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIRECTORY.parent / ".env")

# number of years to go back, make sure there was a Billboard chart published
YEARS_AGO = 20
PAGE_URL = "https://www.billboard.com/charts/hot-100/"
# the scope required by the Spotify API, to allow the creation and modification of playlists
SCOPE = "playlist-modify-private"
# Spotify permits HTTP redirects for loopback IP addresses, not localhost.
REDIRECT_URL = "http://127.0.0.1:8888/callback"


def get_date():
    """Returns the date in the past as STR, as going back the defined amount of years."""
    today = dt.date.today()
    try:
        past_date = today.replace(year=today.year - YEARS_AGO)
    except ValueError:
        past_date = today.replace(year=today.year - YEARS_AGO, day=28)
    return past_date.isoformat()


def load_site(past_date):
    """Takes a date as STR and scrapes the defined site, returns songs and artists as LISTs."""
    page_url = PAGE_URL + past_date
    response = requests.get(
        url=page_url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    chart_rows = soup.select(".chart-results-list li.o-chart-results-list__item")
    songs = []
    artists = []
    for row in chart_rows:
        song = row.select_one("h3#title-of-a-story")
        artist = row.select_one("span.c-label")
        if song is not None and artist is not None:
            songs.append(song.get_text(strip=True))
            artists.append(artist.get_text(strip=True))

    if not songs:
        raise ValueError(
            f"No Billboard chart entries found for {past_date}; the chart may be "
            "unavailable or its page structure may have changed."
        )
    return songs, artists


# calculate the date in the past
date = get_date()
# get lists of songs and artists for that year
song_list, artist_list = load_site(date)

# Require Spotify credentials before starting OAuth.
spotify_id = os.getenv("SPOTIFY_ID")
spotify_secret = os.getenv("SPOTIFY_SECRET")
if not spotify_id or not spotify_secret:
    raise RuntimeError(
        f"Add SPOTIFY_ID and SPOTIFY_SECRET to {SCRIPT_DIRECTORY.parent / '.env'}."
    )

# authorize through spotipy, at the first run this will open the web browser for confirmation and generate token.txt
oauth = SpotifyOAuth(scope=SCOPE, redirect_uri=REDIRECT_URL,
                     client_id=spotify_id,
                     client_secret=spotify_secret,
                     show_dialog=True, cache_path=str(SCRIPT_DIRECTORY / "token.txt"))
sp = spotipy.Spotify(auth_manager=oauth)

song_urls = []
for song, artist in zip(song_list, artist_list):
    result = sp.search(q=f"track:{song} artist:{artist}", type="track", limit=1)
    if result is None:
        raise RuntimeError(f"Spotify returned no search response for {song}.")
    tracks = result.get("tracks") or {}
    items = tracks.get("items") or []
    track_uri = items[0].get("uri") if items else None
    if isinstance(track_uri, str):
        song_urls.append(track_uri)
    else:
        print(f"{song} by {artist} doesn't seem to exist in Spotify.")

if not song_urls:
    raise RuntimeError("Spotify search found no matching tracks; no playlist was created.")

# get the user ID
current_user = sp.current_user()
if current_user is None:
    raise RuntimeError("Spotify returned no current-user response.")

user_id = current_user.get("id")
if not isinstance(user_id, str):
    raise RuntimeError("Spotify did not return a user ID; cannot create the playlist.")

# create the playlist
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
if playlist is None:
    raise RuntimeError("Spotify returned no playlist response.")

playlist_id = playlist.get("id")
if not isinstance(playlist_id, str):
    raise RuntimeError("Spotify did not return a playlist ID; cannot add tracks.")

# add the songs
sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=song_urls)
