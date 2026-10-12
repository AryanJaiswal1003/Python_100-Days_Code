from multiprocessing import Value
from tokenize import StringPrefix

from bs4 import BeautifulSoup
import requests

response = requests.get("https://appbrewery.github.io/news.ycombinator.com/", timeout=15)
# Parse the downloaded HTML so Beautiful Soup can search its elements.
soup = BeautifulSoup(response.text, "html.parser")

# Collect every article title link and its corresponding score from the page.
articles = soup.find_all(name="a", class_="storylink")
scores = soup.find_all(name="span", class_="score")

# Stop with a clear message if the page no longer has the elements we expect.
if not articles:
    raise ValueError("No article links found; the page's HTML selector may have changed")
if not scores:
    raise ValueError("No article scores found; the page's HTML selector may have changed")


# Keep article titles and links in separate lists, using the same order as the page.
article_texts = []
article_links = []

for article_tag in articles:
    # get_text() returns the visible title; strip=True removes surrounding whitespace.
    text = article_tag.get_text(strip = True)
    article_texts.append(text)

    # The article's URL is stored in the anchor element's href attribute.
    link = article_tag.get("href")
    article_links.append(link)

# Extract the leading number from each score (for example, "38 points" -> 38).
article_upvotes = [int(score.get_text(strip=True).split()[0]) for score in scores]


# Find the largest score and its position so we can retrieve that article's details.
largest_num = max(article_upvotes)
largest_index = article_upvotes.index(largest_num)

# The three lists share page order, so largest_index identifies the same article in each.
print(f"Article Text - {article_texts[largest_index]} \n Article Link - {article_links[largest_index]} \n Upvotes - {largest_num}")
