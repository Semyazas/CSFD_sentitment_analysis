from Create_tables import Create_database
from Collect_movies_data import Collect_movies
from Collect_user_data import Collect_users

if __name__ == "__main__":
    Create_database()
    Collect_movies()
    Collect_users()