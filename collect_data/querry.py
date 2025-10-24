import sqlite3

def main() -> None:    
    conn = sqlite3.connect('movie_reviews.db')

    # Create a cursor
    c = conn.cursor()

    # Create a table
    c.execute("""
        SELECT username, rating
        FROM reviews
        LIMIT 5;
    """)
    print(c.fetchall())

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()