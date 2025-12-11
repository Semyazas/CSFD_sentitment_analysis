import sqlite3
from Scrappers.UserProfileScrapper import UserProfileScrapper 
from multiprocessing import Process

def process_batch(data_batch):
    # create resources inside the process
    conn = sqlite3.connect('movie_reviews.db')
    c = conn.cursor()
    scraper = UserProfileScrapper(cursor=c)

    scraper.get_user_data(data_batch)

    conn.commit()
    conn.close()

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
    processes = []
    batch_size = len(data) // 3

    for i in range(0, len(data), batch_size):
        data_batch = data[i:i + batch_size]
        print(f"Starting batch {i} to {i + batch_size}")

        p = Process(target=process_batch, args=(data_batch,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
    

if __name__ == "__main__":
    main()