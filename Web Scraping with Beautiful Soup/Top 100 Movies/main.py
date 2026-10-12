import io
import sys

import requests
from bs4 import BeautifulSoup

URL = "https://web.archive.org/web/20200518073855/https://www.empireonline.com/movies/features/best-movies-2/"

# Download the page HTML and parse it so Beautiful Soup can search the page.
response = requests.get(URL)
website_html = response.text

soup = BeautifulSoup(website_html, "html.parser")
# Find each movie heading and keep only its visible text, not the <h3> markup.
movies = all_movies = [
    movie.get_text(strip=True)
    for movie in soup.find_all(name="h3", class_="title")
]

# Stop early with a clear error if the page structure or selector has changed.
if not movies:
    raise ValueError("No article links found; the page's HTML selector may have changed")

# Configure the console to display titles containing characters outside cp1252.
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

# Reverse the page order to list the movies from 1 through 100.
movies = movies[::-1]

# Save one title per line; UTF-8 supports all characters in the scraped titles.
with open("Web Scraping with Beautiful Soup/Top 100 Movies/movies.txt", mode="w", encoding="utf-8") as file:
    for movie in movies:
        file.write(f"{movie}\n")