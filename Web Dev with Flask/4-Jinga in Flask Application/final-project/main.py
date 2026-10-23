from flask import Flask, render_template
from post import Post
import requests

# The source data starts as dictionaries, similar to data from an API.
BLOGS = [
    {
        "id": 1,
        "title": "The Life of Cactus",
        "subtitle": "Who knew that cacti lived such interesting lives.",
        "body": (
            "Nori grape silver beet broccoli kombu beet greens fava bean potato "
            "quandong celery. Bunya nuts black-eyed pea prairie turnip leek lentil "
            "turnip greens parsnip. Sea lettuce lettuce water chestnut eggplant "
            "winter purslane fennel azuki bean earthnut pea sierra leone bologi "
            "leek soko chicory celtuce parsley jícama salsify."
        ),
    },
    {
        "id": 2,
        "title": "Top 15 Things to do When You are Bored",
        "subtitle": "Are you bored? Don't know what to do? Try these top 15 activities.",
        "body": (
            "Chase ball of string eat plants, meow, and throw up because I ate "
            "plants going to catch the red dot today going to catch the red dot "
            "today. I could pee on this if I had the energy. Chew iPad power cord "
            "steal the warm chair right after you get up for purr for no reason "
            "leave hair everywhere, decide to want nothing to do with my owner today."
        ),
    },
    {
        "id": 3,
        "title": "Introduction to Intermittent Fasting",
        "subtitle": "Learn about the newest health craze.",
        "body": (
            "Cupcake ipsum dolor. Sit amet marshmallow topping cheesecake muffin. "
            "Halvah croissant candy canes bonbon candy. Apple pie jelly beans "
            "topping carrot cake danish tart cake cheesecake. Muffin danish "
            "chocolate soufflé pastry icing bonbon oat cake. Powder cake jujubes "
            "oat cake. Lemon drops tootsie roll marshmallow halvah carrot cake."
        ),
    },
]
# Convert each dictionary into a Post object so templates can use dot notation.
posts = BLOGS
post_objects = []

for post in posts:
    post_obj = Post(post["id"], post["title"], post["subtitle"], post["body"])
    post_objects.append(post_obj)

# Flask serves templates from the sibling templates folder by default.
app = Flask(__name__)

@app.route('/')
def home():
    # all_posts is available in index.html for the Jinja for-loop.
    return render_template("index.html", all_posts=post_objects)

@app.route('/post/<int:index>')
def show_post(index):
    # <int:index> converts the URL segment to an integer before this runs.
    requested_post = None
    for blog_post in post_objects:
        if blog_post.id == index:
            requested_post = blog_post
    # The template receives either the matching Post object or None.
    return render_template("post.html", post=requested_post)

if __name__ == "__main__":
    app.run(debug=True)
