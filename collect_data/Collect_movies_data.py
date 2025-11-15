import sqlite3
from Scrappers.MovieReviewScraper import MovieReviewScraper
from Scrappers.UrlFinder import UrlFinder

def collect_data_for_movies_from_genres(
        genres: list[str],
        number_of_movies_from_genre : int  = 10,
        number_of_pages_to_scroll : int = 10) -> None:
    url_scrapper = UrlFinder()
    movies = url_scrapper.scrap_url_from_genres(
        genres,
        number_of_movies_from_genre
    )  
    movie_scrapper = MovieReviewScraper()
    for i,movie_url in enumerate(movies):
        genre = genres[i // number_of_movies_from_genre]
        print(f"Collecting data for movie: {movie_url} of genre {genre}, number_of_pages_to_scroll: {number_of_pages_to_scroll} ")
        collect_data_for_movie(
            movie_url,
            number_of_pages_to_scroll,
            genre[0],
            scrapper= movie_scrapper            
        )

def collect_data_for_movie(
        movie_url: str,
        number_of_pages : int,
        genre : str,
        scrapper: MovieReviewScraper) -> None:
    should_retry = True
    page_num = 1
    while should_retry:
        should_retry, page_num = scrapper.\
            scrap_CSFD_reviews_from_movie(
                movie_url[:-8] + "recenze/", 
                genre,
                number_of_pages,
                page = page_num
            )
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
        number_of_movies_from_genre = 10,
        number_of_pages_to_scroll = 10
    )
    conn.close()
if __name__ == "__main__":
    main()