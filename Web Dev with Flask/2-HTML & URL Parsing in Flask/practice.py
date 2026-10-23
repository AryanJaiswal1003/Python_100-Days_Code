from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1 style="text-align: center">HAPPY BIRTHDAY!</h1>' \
            '<p>Happy Birthday to You!!!</p>' \
            '<img src="https://mir-s3-cdn-cf.behance.net/project_modules/hd/9193d483500913.5d3ecfc94f929.gif", width=500px>'

# Different routes using the app.route decorator
@app.route('/bye')
def bye():
    return "Bye!"

# Creating variable paths and converting the path to a specified data type
@app.route('/username/<name>/<int:number>')
def greet(name, number):
    return f"Hello there {name}!!, you are {number} years old"

if __name__ == "__main__":
    # Running the app in debug mode to auto reload
    app.run(debug=True)