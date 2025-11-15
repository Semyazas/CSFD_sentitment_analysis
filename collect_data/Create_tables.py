import sqlite3


def main():
    conn = sqlite3.connect('movie_reviews.db')
    c = conn.cursor()
    # Ensure `reviews` table exists with the desired column order.
    c.execute('''CREATE TABLE  reviews(
            username TEXT,
            rating INT,
            review_text TEXT,
            movie_name TEXT,
            user_ref TEXT UNIQUE
        );''')

    conn.commit()

    c.execute('''CREATE TABLE  movies(
        movie_name TEXT,
        genre TEXT,
        average_rating TEXT
    );''')
    conn.commit()

    c.execute('''CREATE TABLE users(
        username TEXT,
        total_reviews INT,
        since_when TEXT,
        place TEXT,
        user_ref TEXT UNIQUE
    );''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()

