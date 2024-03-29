import orm

async def add_user(user_id, username):
    existing_user = orm.session.query(orm.Users.user_id).filter_by(user_id=user_id).first()

    if existing_user is None:
        new_user = orm.Users(user_id=user_id, username=username)
        orm.session.add(new_user)
        orm.session.commit()

async def save_movie(movie_data):
    id = int(movie_data["id"])
    name = str(movie_data["names"][0]["name"])
    rating = float(movie_data["rating"]["imdb"])
    year = int(movie_data["year"])
    description = str(movie_data["description"])
    try:
        trailer_url = str(movie_data["videos"]["trailers"][0]["url"])
    except BaseException:
        trailer_url = ""
    # trailer_url = str(movie_data["videos"]["trailers"][0]["url"])
    poster_url = str(movie_data["poster"]["url"])

    new_movie = orm.Movies(movie_id=id, movie_name=name, movie_rating=rating,
                           movie_year=year, description=description, url=trailer_url, poster=poster_url)
    

    try:
        orm.session.add(new_movie)
        orm.session.commit()
    except orm.IntegrityError as e:
        # Если возникает ошибка из-за нарушения ограничения уникальности,
        # откатываем транзакцию и логируем ошибку
        # await orm.session.rollback()
        print(f"Ошибка при сохранении фильма: {e}")

async def get_movie_by_id(movie_id: int):
    """
    Получает фильм из базы данных по его movie_id.
    Возвращает объект фильма или None, если фильм не найден.
    """
    try:
        # Используем метод query.get() для получения фильма по его movie_id
        movie = orm.session.query(orm.Movies).filter(orm.Movies.movie_id == movie_id).first()
        return movie
    except Exception as e:
        print(f"Ошибка при получении фильма: {e}")
        return None

async def add_liked_movie(user_id, movie_id):
    liked_movie = orm.LikedMovies(user_id=user_id, movie_id=movie_id)
    orm.session.add(liked_movie)
    orm.session.commit()

async def add_disliked_movie(user_id, movie_id):
    disliked_movie = orm.DislikedMovies(user_id=user_id, movie_id=movie_id)
    orm.session.add(disliked_movie)
    orm.session.commit()

async def get_liked_movies_for_user(user_id):
    liked_movies = orm.session.query(orm.Movies.movie_name).\
        join(orm.LikedMovies, orm.LikedMovies.movie_id == orm.Movies.movie_id).\
        filter(orm.LikedMovies.user_id == user_id).all()

    # Извлечение названий фильмов и возврат списка
    movie_names = [movie.movie_name for movie in liked_movies]
    return movie_names

async def get_disliked_movies_for_user(user_id):
    disliked_movies = orm.session.query(orm.Movies.movie_id).\
        join(orm.DislikedMovies, orm.DislikedMovies.movie_id == orm.Movies.movie_id).\
        filter(orm.DislikedMovies.user_id == user_id).all()

    # Извлечение названий фильмов и возврат списка
    movie_ids = [movie.movie_id for movie in disliked_movies]
    return movie_ids

async def get_movie_in_one_string(movie_id):
    movie = orm.session.query(orm.Movies).filter(
        orm.Movies.movie_id == movie_id).first()
    name = movie.movie_name
    rating = str(movie.movie_rating)
    year = str(movie.movie_year)
    description = movie.description
    trailer_url = f"<a href='{movie.url}'>Трейлер</a>"

    final_list = [name, rating, year, description, trailer_url]

    return "\n".join(final_list)


async def get_poster_url(movie_id):
    movie = orm.session.query(orm.Movies).filter(
        orm.Movies.movie_id == movie_id).first()
    
    return movie.poster

async def delete_from_liked(user_id, movie_id):
    # Выполнение запроса для удаления записи
    orm.session.query(orm.LikedMovies).filter(
        orm.LikedMovies.user_id == user_id,
        orm.LikedMovies.movie_id == movie_id
    ).delete(synchronize_session=False)

    orm.session.commit()

async def get_movie_id(movie_name):
    # Выполнение запроса для получения movie_id по movie_name
    movie = orm.session.query(orm.Movies).filter(
        orm.Movies.movie_name == movie_name
    ).first()
    
    if movie is not None:
        return movie.movie_id
    else:
        return None
    
async def collections_empty():
    return orm.session.query(orm.Collections).first() is None

async def save_collection(item):
    category = item["category"]
    name = item["name"]
    slug = item["slug"]

    new_collection = orm.Collections(category=category, name=name, slug=slug)
    orm.session.add(new_collection)
    orm.session.commit()


async def get_collections():
    return orm.session.query(orm.Collections).all()

async def get_slug_on_collection_name(name):
    return orm.session.query(orm.Collections).filter(orm.Collections.name == name).first().slug