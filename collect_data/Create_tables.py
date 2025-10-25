import sqlite3


def main():
    conn = sqlite3.connect('movie_reviews.db')
    c = conn.cursor()
    # Ensure `reviews` table exists with the desired column order.
    c.execute('''CREATE TABLE IF NOT EXISTS reviews(
            username TEXT,
            rating INT,
            review_text TEXT,
            movie_name TEXT
        );''')

    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS movies(
        movie_name TEXT,
        genre TEXT,
        average_rating TEXT
    );''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS users(
        username TEXT,
        total_reviews INT,
        average_rating REAL
    );''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()

