# Import Path for handling file paths in a cross‑platform way
from pathlib import Path
import re   # Regular expressions for pattern matching in attributes/text

# Import BeautifulSoup and Tag for parsing and navigating HTML
from bs4 import BeautifulSoup, Tag


# Helper function to print outputs with a title label
def show(title: str, value: object) -> None:
    print(f"\n--- {title} ---")  # Print a header for clarity
    print(value)                 # Print the actual value


def main() -> None:
    # Load the HTML file that sits beside this script (same folder).
    html_path = Path(__file__).with_name("website.html")
    html = html_path.read_text(encoding="utf-8")

    # Parse the HTML into a BeautifulSoup object
    soup = BeautifulSoup(html, "html.parser")

    # --- Basic document inspection ---
    show("Formatted HTML (first 300 characters)", soup.prettify()[:300])  # Pretty print first 300 chars
    show("First anchor via direct tag access", soup.a)                   # First <a> tag
    show("Page title", soup.title.get_text(strip=True) if soup.title else None)  # <title> text
    show("First h1", soup.h1)                                            # First <h1> tag
    if soup.h1:
        # Show details about the <h1> tag
        show("Tag name, attributes, and id", (soup.h1.name, soup.h1.attrs, soup.h1.get("id")))
        show("h1's direct string", soup.h1.string)
    show("Body text", soup.body.get_text(" ", strip=True) if soup.body else None)  # All text inside <body>

    # --- Finding tags with filters ---
    show("First h3 with class=heading", soup.find("h3", class_="heading"))
    show("All links", soup.find_all("a"))
    show("All h1 and h3 tags", soup.find_all(["h1", "h3"]))
    show("First two links", soup.find_all("a", limit=2))
    show("Links whose href starts with https", soup.find_all(href=re.compile(r"^https://")))
    show("Text node matching Angela Yu", soup.find(string="Angela Yu"))
    show("Text nodes containing Bootcamp", soup.find_all(string=re.compile("Bootcamp")))

    # --- CSS selector queries ---
    show("Element with id=name", soup.select_one("#name"))               # Select by id
    show("All heading elements with class=heading", soup.select("h3.heading"))  # Select by class
    show("Links with an href attribute", soup.select("a[href]"))         # Select by attribute
    show("Links inside paragraphs", soup.select("p a"))                  # Select nested tags

    # --- Extract text and attributes from first link ---
    first_link = soup.find("a")
    if first_link:
        show("First link text", first_link.get_text(" ", strip=True))
        show("First link href via get()", first_link.get("href"))
        show("Does first link have href?", first_link.has_attr("href"))
        show("All first-link href values", first_link.get_attribute_list("href"))
        show("First link attributes", first_link.attrs)

    # --- Text nodes in the document ---
    show("All text nodes", list(soup.strings))              # Includes whitespace
    show("Non-empty, whitespace-trimmed text nodes", list(soup.stripped_strings))

    # --- Tree traversal examples ---
    first_list = soup.find("ul")
    if first_list:
        show("Direct children of the list (including whitespace)", list(first_list.children))
        show("Direct list-item children", [child for child in first_list.children if isinstance(child, Tag)])
        show("All descendants of the list", list(first_list.descendants))
        show("List items only (recursive=False)", first_list.find_all("li", recursive=False))

    # --- Navigating relatives of a heading ---
    first_heading = soup.find("h3", class_="heading")
    if first_heading:
        show("Heading's parent tag", first_heading.parent.name if first_heading.parent else None)
        show("Heading's ancestors", [ancestor.name for ancestor in first_heading.parents])
        show("Heading's body ancestor", first_heading.find_parent("body"))
        show("Heading's next element", first_heading.next_element)
        show("Heading's next link", first_heading.find_next("a"))
        show("Heading's next sibling", first_heading.find_next_sibling())
        show("Heading's previous sibling", first_heading.find_previous_sibling())
        show("All next siblings", first_heading.find_next_siblings())
        show("All previous siblings", first_heading.find_previous_siblings())
        show("All following links", first_heading.find_all_next("a"))
        show("All preceding headings", first_heading.find_all_previous(["h1", "h3"]))

    # --- Convert scraped elements into Python data structures ---
    links = [
        {"text": link.get_text(" ", strip=True), "url": link.get("href")}
        for link in soup.find_all("a", href=True)
    ]
    headings = [
        heading.get_text(" ", strip=True)
        for heading in soup.select("h1, h2, h3, h4, h5, h6")
    ]
    show("Scraped links as dictionaries", links)
    show("Scraped headings", headings)


# Entry point of the script
if __name__ == "__main__":
    main()