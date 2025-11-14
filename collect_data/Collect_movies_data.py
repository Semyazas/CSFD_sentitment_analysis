import sqlite3
from Scrappers.MovieReviewScraper import MovieReviewScraper
from Scrappers.UrlFinder import UrlFinder

def collect_data_for_movies_from_genres(
        genres: list[str],
        conn : sqlite3.Connection,
        number_of_movies_from_genre : int  = 10,
        number_of_pages_to_scroll : int = 10) -> None:
    url_scrapper = UrlFinder()
    movies = url_scrapper.scrap_url_from_genres(
        genres,
        number_of_movies_from_genre
    )  
    conn = sqlite3.connect('movie_reviews.db')
    movie_scrapper = MovieReviewScraper()
    for i,movie_url in enumerate(movies):
        genre = genres[i // number_of_movies_from_genre]
        print(f"Collecting data for movie: {movie_url} of genre {genre}, number_of_pages_to_scroll: {number_of_pages_to_scroll} ")
        collect_data_for_movie(
            movie_url,
            conn,
            number_of_pages_to_scroll,
            genre[0],
            scrapper= movie_scrapper            
        )
def add_data_to_reviews_table(
        conn : sqlite3.Connection,
        reviews_data : list[tuple[str, str, str, str, str]]) -> None:
    c = conn.cursor()
    # username, rating, review_text, movie_name
    # Create a table
    c.executemany("""
        INSERT OR IGNORE INTO reviews (
            username,
            rating, 
            review_text, 
            movie_name,
            user_ref
        ) VALUES (?, ?, ?, ?, ?)
        """, 
        reviews_data
    )
    conn.commit()

def add_data_to_movies_table(
        conn : sqlite3.Connection,
        movie_name : str,
        genre : str,
        average_rating : float) -> None:
    c = conn.cursor()
    c.execute("""
        INSERT INTO movies (
            movie_name,
            genre,
            average_rating
        ) VALUES (?, ?, ?)""",
        (movie_name, genre, average_rating))
    conn.commit()
        

def collect_data_for_movie(
        movie_url: str,
        conn : sqlite3.Connection,
        number_of_pages : int,
        genre : str,
        scrapper: MovieReviewScraper) -> None:

    data = scrapper.\
        scrap_CSFD_reviews_from_movie(movie_url[:-8] + "recenze/", number_of_pages)

    movies_data, avg_rating = data["reviews"], data["average_rating"]
    print(f"Average rating for {movie_url}: {avg_rating}")
    movie = movies_data[0][3]
    print(f"Movie name extracted: {movie} genre: {genre} ")
    
    add_data_to_reviews_table(conn, movies_data)
    add_data_to_movies_table(conn, movie, genre, avg_rating)

def main():
    conn = sqlite3.connect('movie_reviews.db')
    genres = [
        ("Thriller",False),
        ("Komedie",False),
        ("Drama",False),
        ("Horor",False),
        ("Sci-Fi",False),
        ("Fantasy",False)
    ]
    collect_data_for_movies_from_genres(
        genres,
        conn,
        number_of_movies_from_genre = 10,
        number_of_pages_to_scroll = 10
    )
    conn.close()
if __name__ == "__main__":
    main()