from flask import Flask, jsonify, render_template
import random
import datetime
import requests


# Flask uses this module location to find the templates folder.
app = Flask(__name__)

# Sample blog data used by both the JSON endpoint and Jinja templates.
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
# Keep the name used in the lesson's template-rendering example.
all_posts = BLOGS


@app.route('/')
def home():
    # These values are sent to index.html and can be displayed with {{ ... }}.
    random_num = random.randint(1, 10)
    current_year = datetime.datetime.now().year
    return render_template("index.html", num=random_num, year=current_year)

@app.route('/guess/<name>')
def guess(name):
    # The URL value <name> is passed into this function by Flask.
    # These public APIs provide example data for the guess.html template.
    gender_url = f"https://api.genderize.io?name={name}"

    gender_response = requests.get(gender_url)
    gender_data = gender_response.json()
    gender = gender_data["gender"]

    age_url = f"https://api.agify.io?name={name}"

    age_response = requests.get(age_url)
    age_data = age_response.json()
    age = age_data["age"]

    return render_template("guess.html", person_name=name, gender=gender, age=age)


@app.route('/api/blogs')
def blogs():
    # jsonify converts the Python list into an HTTP JSON response.
    return jsonify(BLOGS)


@app.route('/blog/<num>')
def get_blog(num):
    # Follow-up: use num to select a post when practicing dynamic Jinja pages.
    # The current lesson intentionally passes every post to blog.html.
    return render_template("blog.html", posts=all_posts)


if __name__ == "__main__":
    app.run(debug=True)