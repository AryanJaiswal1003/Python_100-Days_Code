from flask import Flask, redirect, render_template, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, URL
import csv
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
cafe_data_path = Path(app.root_path) / "cafe-data.csv"


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location = StringField('Cafe Location on Google Maps (URL)', validators=[DataRequired(), URL()])
    open = StringField('Opening Time 8 AM', validators=[DataRequired()])
    close = StringField('Closing Time 9:30 PM', validators=[DataRequired()])

    coffee_rating = SelectField("Coffee Rating", choices=[
        ("1", "☕️"),
        ("2", "☕☕"),
        ("3", "☕☕☕"),
        ("4", "☕☕☕☕"),
        ("5", "☕☕☕☕☕"),
    ], validators=[DataRequired()])
    wifi_rating = SelectField("WIFI Strength Rating", choices=[
        ("N/A", "✘"),
        ("1", "💪"),
        ("2", "💪💪"),
        ("3", "💪💪💪"),
        ("4", "💪💪💪💪"),
        ("5", "💪💪💪💪💪")
    ], validators=[DataRequired()])
    power_rating = SelectField("Power Socket Availability", choices=[
        ("N/A", "✘"),
        ("1", "🔌"),
        ("2", "🔌🔌"),
        ("3", "🔌🔌🔌"),
        ("4", "🔌🔌🔌🔌"),
        ("5", "🔌🔌🔌🔌🔌")
    ], validators=[DataRequired()])

    submit = SubmitField('Submit')

# Exercise:
# add: Location URL, open time, closing time, coffee rating, wifi rating, power outlet rating fields
# make coffee/wifi/power a select element with choice of 0 to 5.
#e.g. You could use emojis ☕️/💪/✘/🔌
# make all fields required except submit
# use a validator to check that the URL field has a URL entered.
# ---------------------------------------------------------------------------


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add')
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        with cafe_data_path.open(mode="a", encoding="utf-8") as csv_file:
            csv_file.write(f"\n{form.cafe.data},"
                           f"{form.location.data},"
                           f"{form.open.data},"
                           f"{form.close.data},"
                           f"{form.coffee_rating.data},"
                           f"{form.wifi_rating.data},"
                           f"{form.power_rating.data}")
            return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    with cafe_data_path.open(newline='', encoding='utf-8') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows)


if __name__ == '__main__':
    app.run(debug=True, port=5002)
