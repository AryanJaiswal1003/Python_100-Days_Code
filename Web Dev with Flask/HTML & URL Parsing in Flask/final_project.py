from flask import Flask
import random

# This generates a random number between 0 and 9. The number is chosen once when the program starts.
random_num = random.randint(0, 9)
print(random_num)  # Shows the random number in the terminal for testing

# Create the Flask app object. This object handles all routes and web requests.
app = Flask(__name__)

# Route for the home page.
# When the user opens the website with just the domain name, this function is called and returns the HTML page.
@app.route('/')
def home():
    # This returns HTML content to display on the homepage. It includes a heading and a GIF.
    return "<h1>Guess a Number between 0 & 9</h1>" \
            "<img src='https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXppdGJwYnNlc3FpaHhuMHhvc2I2MXN5ZDh2ejRzaTAxcDBvcGx4ciZlcD12MV9pbnRlcm5hbF9naWJfYnlfaWQmY3Q9Zw/vK1p6B4hV6MhGNC2co/giphy.gif'/>"

# Route for guessing the random number.
# The URL is like /5, /8, /2, etc.
# The integer part after the slash is passed to the function as guess.
@app.route("/<int:guess>")
def guess_number(guess):
    # If the guessed number is greater than the random number,
    # show a "Too High" message.
    if guess > random_num:
        return "<h1 style='color: purple'>Too High. Try Again!!</h1>" \
                "<img src='https://media.giphy.com/media/3o7aCSPqXE5C6T8tBC/giphy.gif'/>"

    # If the guessed number is smaller than the random number,
    # show a "Too low" message.
    elif guess < random_num:
        return "<h1 style='color: red'>Too low, Try Again!!</h1>" \
                "<img src='https://media.giphy.com/media/jD4DwBtqPXRXa/giphy.gif'/>"

    # If the guessed number matches the random number,
    # show a success message and celebration GIF.
    else:
        return "<h1 style='color: green'>You Found Me!</h1>" \
                "<img src='https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZnJsbWdyaGt3M3lqdGZwZnRsZGxyZHQ3ajRkYzJwc2F3eXpreGd6aSZlcD12MV9pbnRlcm5hbF9naWJfYnlfaWQmY3Q9Zw/1TM8yYG2kMInpK69Rc/giphy.gif'/>"

# This makes sure the app runs only when this file is executed directly.
# It starts the Flask development server.
if __name__ == "__main__":
    app.run(debug=True)