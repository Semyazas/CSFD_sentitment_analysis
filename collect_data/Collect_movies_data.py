import sqlite3
from Scrap import Scrapper

def collect_data_for_movies_from_genres(
        genres: list[str],
        conn : sqlite3.Connection,
        number_of_movies_from_genre : int  = 5,
        number_of_pages_to_scroll : int = 5) -> None:
    scrapper = Scrapper()
    movies = scrapper.scrap_url_from_genres(
        genres,
        number_of_movies_from_genre
    )  
    conn = sqlite3.connect('movie_reviews.db')
    for i,movie_url in enumerate(movies):
        genre = genres[i // number_of_movies_from_genre]
        print(f"Collecting data for movie: {movie_url} of genre {genre}")
        collect_data_for_movie(
            movie_url,
            conn,
            number_of_pages_to_scroll,
            genre[0]              
        )
    
def collect_data_for_movie(
        movie_url: str,
        conn : sqlite3.Connection,
        number_of_pages : int,
        genre : str) -> None:
    scrapper = Scrapper()
    data = scrapper.\
        scrap_CSFD_reviews_from_movie(movie_url + "recenze/", number_of_pages)

    movies_data, avg_rating = data["reviews"], data["average_rating"]
    print(f"Average rating for {movie_url}: {avg_rating}")
    movie = movie_url.split("/")[-2].split("-")
    movie = " ".join([word.capitalize() for word in movie[1:]])
    print(f"Movie name extracted: {movie} genre: {genre} ")
    c = conn.cursor()
    # username, rating, review_text, movie_name
    # Create a table
    c.executemany("""
        INSERT OR IGNORE INTO reviews (
            username,
            rating, 
            review_text, 
            movie_name
        ) VALUES (?, ?, ?, ?)
        """, 
        movies_data
    )
    print(c.fetchall())
    conn.commit()

    c.execute("""
        INSERT INTO movies (
            movie_name,
            genre,
            average_rating
        ) VALUES (?, ?, ?)""",
        (movie, genre, avg_rating))
    conn.commit()
def main():
    conn = sqlite3.connect('movie_reviews.db')
    genres = [

        ("Thriller",False)
    ]
    collect_data_for_movies_from_genres(
        genres,
        conn,
        number_of_movies_from_genre = 5,
        number_of_pages_to_scroll = 5
    )
    conn.close()
if __name__ == "__main__":
    main()