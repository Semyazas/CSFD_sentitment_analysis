import sqlite3
from Scrappers.UserProfileScrapper import UserProfileScrapper 

def main() -> None:    
    conn = sqlite3.connect('movie_reviews.db')

    # Create a cursor
    c = conn.cursor()

    # Create a table
    c.execute("""
        SELECT DISTINCT(username), user_ref
        FROM reviews
    """)
    data = c.fetchall()
    print("Number of users to scrape:", len(data))
    print(data[0])

    conn.commit()

    Scrapper = UserProfileScrapper()
    Scrapper.get_user_data(data,c)

if __name__ == "__main__":
    main()