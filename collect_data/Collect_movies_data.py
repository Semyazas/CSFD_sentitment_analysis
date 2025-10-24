import sqlite3
from Scrap import Scrapper

def collect_data_for_movie(
        movie_url: str,
        conn : sqlite3.Connection
        ) -> None:
    scrapper = Scrapper()
    movies_data = scrapper.scrap_CSFD_reviews_from_movie(movie_url + "recenze/")

        # Create a cursor
    c = conn.cursor()
    # username, rating, review_text, movie_name
    # Create a table
    c.executemany("""
        INSERT INTO reviews (
            username,
            rating,
            review_text,
            movie_name
        ) VALUES (?, ?, ?, ?)""", movies_data)
    print(c.fetchall())

    conn.commit()

def main():
    conn = sqlite3.connect('movie_reviews.db')
    collect_data_for_movie(
        "https://www.csfd.cz/film/3037-inception/",
        conn
    )
    conn.close()

if __name__ == "__main__":
    main()