from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100))
	complete = db.Column(db.Boolean)

@app.route('/', methods = ['GET', 'POST'])
def index():
	todo_list = Todo.query.all()
	raw_quote = requests.get('https://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en')
	quote_obj = raw_quote.json()
	quote = quote_obj['quoteText']
	author = quote_obj['quoteAuthor']

	if request.method == "POST":
		city = request.form['city']
		country = request.form['country']
		api_key = "87bf95f5662f1c7847c31c6c3d2b8a62"

		weather_url = requests.get(f'http://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={city},{country}&units=imperial')
		weather_data = weather_url.json()

		temp = round(weather_data['main']['temp'])
		humidity = weather_data['main']['humidity']
		wind_speed = weather_data['wind']['speed']
		max_temp = weather_data['main']['temp_max']
		min_temp = weather_data['main']['temp_min']
		main_desc = weather_data['weather'][0]['main']
		extra_desc = weather_data['weather'][0]['description']
		icon_url = "http://openweathermap.org/img/wn/" + str(weather_data['weather'][0]['icon']) + "@2x.png"

		return render_template("result.html", todo_list=todo_list, quote=quote, author=author, temp=temp, max_temp=max_temp, min_temp=min_temp, humidity=humidity, wind_speed=wind_speed, icon_url=icon_url, main_desc=main_desc, extra_desc=extra_desc, city=city)

	return render_template("weathersearch.html", todo_list=todo_list, quote=quote, author=author)

@app.route("/add", methods=["POST"])
def add():
	title = request.form.get("title")
	new_todo = Todo(title=title, complete=False)
	db.session.add(new_todo)
	db.session.commit()
	return redirect(url_for("index"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
	todo = Todo.query.filter_by(id=todo_id).first()
	todo.complete = not todo.complete
	db.session.commit()
	return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
	todo = Todo.query.filter_by(id=todo_id).first()
	db.session.delete(todo)
	db.session.commit()
	return redirect(url_for("index"))

if __name__ == "__main__":
	db.create_all()
	app.run(debug=True)