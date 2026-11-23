from models import db, User, Movie

class DataManager:
    def get_users(self):
        """Fetches all users from database."""
        return User.query.all()

    def get_user(self, user_id):
        """Fetches a single user by ID."""
        return User.query.get(user_id)

    def create_user(self, name):
        """Creates and saves a new user."""
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    def get_movies(self, user_id):
        """Fetches all movies for a given user."""
        return Movie.query.filter_by(user_id=user_id).all()

    def get_movie(self, movie_id):
        """Fetches a single movie by ID."""
        return Movie.query.get(movie_id)

    def add_movie(self, user_id, title, director, year, poster_url):
        """Adds a movie to a specific user's favorites list."""
        new_movie = Movie(
            title=title,
            director=director,
            year=year,
            poster_url=poster_url,
            user_id=user_id
        )
        db.session.add(new_movie)
        db.session.commit()
        return new_movie

    def update_movie(self, movie_id, new_title):
        """Updates the title of a movie."""
        movie = Movie.query.get(movie_id)
        if movie:
            movie.title = new_title
            db.session.commit()
            return movie
        return None

    def delete_movie(self, movie_id):
        """Deletes a movie from the database."""
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return True
        return False
