import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db
from data_manager import DataManager

app = Flask(__name__)
app.secret_key = "super_secret_moviweb_key"

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(basedir, "data")
os.makedirs(db_dir, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(db_dir, 'movies.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
data_manager = DataManager()

with app.app_context():
    db.create_all()

OMDB_API_KEY = "trilogy"  # Replace with your custom OMDb API key if needed


def fetch_omdb_movie(title):
    """Fetches movie info from OMDb API by title."""
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data.get("Response") == "True":
            year = data.get("Year", "")
            # Clean up year string if range (e.g. "1997–2000")
            year_clean = int(year[:4]) if year[:4].isdigit() else None
            return {
                "title": data.get("Title", title),
                "director": data.get("Director", "Unknown"),
                "year": year_clean,
                "poster_url": (
                    data.get("Poster", "") if data.get("Poster") != "N/A" else ""
                ),
            }
    except Exception as e:
        print(f"OMDb Fetch Error: {e}")
    return {"title": title, "director": "Unknown", "year": None, "poster_url": ""}


@app.route("/", methods=["GET"])
def index():
    users = data_manager.get_users()
    movie_counts = {user.id: len(data_manager.get_movies(user.id)) for user in users}
    return render_template("index.html", users=users, movie_counts=movie_counts)


@app.route("/users", methods=["POST"])
def create_user():
    name = request.form.get("name", "").strip()
    if name:
        data_manager.create_user(name)
    return redirect(url_for("index"))


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    data_manager.delete_user(user_id)
    return redirect(url_for("index"))


@app.route("/users/<int:user_id>/movies", methods=["GET"])
def get_movies(user_id):
    user = data_manager.get_user(user_id)
    if not user:
        return render_template("404.html"), 404
    movies = data_manager.get_movies(user_id)
    return render_template("movies.html", user=user, movies=movies)


@app.route("/users/<int:user_id>/movies", methods=["POST"])
def add_movie(user_id):
    user = data_manager.get_user(user_id)
    if not user:
        return render_template("404.html"), 404

    title = request.form.get("title", "").strip()
    if title:
        omdb_data = fetch_omdb_movie(title)
        data_manager.add_movie(
            user_id=user_id,
            title=omdb_data["title"],
            director=omdb_data["director"],
            year=omdb_data["year"],
            poster_url=omdb_data["poster_url"],
        )
    return redirect(url_for("get_movies", user_id=user_id))


@app.route("/users/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_movie(user_id, movie_id):
    new_title = request.form.get("title", "").strip()
    if new_title:
        data_manager.update_movie(movie_id, new_title)
    return redirect(url_for("get_movies", user_id=user_id))


@app.route("/users/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(user_id, movie_id):
    data_manager.delete_movie(movie_id)
    return redirect(url_for("get_movies", user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)