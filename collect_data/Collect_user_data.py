import sqlite3
import Scrap

def main() -> None:    
    conn = sqlite3.connect('movie_reviews.db')

    # Create a cursor
    c = conn.cursor()

    # Create a table
    c.execute("""
        SELECT DISTINCT(username)
        FROM reviews
    """)
    data = c.fetchall()
    data = list(map(lambda x : x[0],data))
    conn.commit()


    Scrapper = Scrap.Scrapper()
    Scrapper.get_user_data(data,c)

if __name__ == "__main__":
    main()