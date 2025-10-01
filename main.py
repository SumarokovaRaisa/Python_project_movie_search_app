from db import get_mysql_connection, get_mongo_collection
from utils import paginate_results, select_genre
from datetime import datetime

genres = ['Action', 'Animation', 'Children', 'Classics', 'Comedy', 'Documentary',
          'Drama', 'Family', 'Foreign', 'Games', 'Horror', 'Music',
          'Sci-Fi', 'Sports', 'Travel', 'New']

# MongoDB collection for storing search queries
mongo_collection = get_mongo_collection()


def save_search(query):
    """ Save a search query in MongoDB with current timestamp.
    :param query: search string (title, genre, year, etc.)"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    mongo_collection.insert_one({"query": query, "datetime": now})

def execute_query(conn, query, params=()):
    """
    Execute SQL query in MySQL and return results.
    :param conn: MySQL connection
    :param query: SQL query string
    :param params: query parameters (tuple)
    :return: fetched results as list of tuples
    """
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

def handle_results(result):
    """ Handle query results: print message if empty or display results
        :param result: query result set"""
    if not result:
        print("No movies found. Try again.")
        return False
    display_results(result)
    return True

def display_results(results, page_size=10):
    """
    Displays results page by page with continuous numbering.
    Asks the user 'Show more?' only if the page is full.
    :param results: list of tuples from SQL query
    :param page_size: number of rows per page
    """
    counter = 1
    for page in paginate_results(results, page_size):
        for row in page:
            print(f"{counter}. {row[0]} ({row[1]}),\nDescription: '{row[2]}'")
            counter += 1
        if len(page) < page_size: # if last page is smaller → stop
            break
        if input("Show more? (y/n): ").lower() != "y":
            break


def search_by_title(conn):
    """
    Searching movie by title or keywords.
    :param conn: MySQL connection
    :return: movie title, year of release and description
    """
    title = input("Enter movie title or keyword: ")
    save_search(title)
    query = """SELECT title, release_year, description
             FROM film
             WHERE title LIKE %s"""
    result = execute_query(conn, query, ("%" + title + "%",))
    handle_results(result)


def search_by_genre(conn):
    """
    Searching movie by genre.
    :param conn: MySQL connection
    :return: movie title, year of release, genre and description
    """
    genre = select_genre(genres)
    save_search(genre)
    query = """SELECT f.title, f.release_year, c.name, f.description
             FROM film f
             JOIN film_category fc ON fc.film_id = f.film_id
             JOIN category c ON fc.category_id = c.category_id
             WHERE LOWER(c.name) = LOWER(%s)"""
    result = execute_query(conn, query, (genre,))
    handle_results(result)


def search_by_year(conn):
    """
    Searching movie by year or range of years (1990 - 2025), using format YYYY-YYYY
    :param conn: MySQL connection
    :return: movie title, year of release, genre and description
    """
    while True:
        years = input("Enter a year or range (e.g. 2006-2008) from 1990 to 2025: ").strip()
        if "-" in years: # Year range
            parts = years.split("-")
            if len(parts) != 2:
                print("Invalid format! Use YYYY-YYYY.")
                continue
            start, end = parts
            if not (start.isdigit() and end.isdigit()):
                print("Years must be numbers!")
                continue
            start, end = int(start), int(end)
            if not (1990 <= start <= 2025 and 1990 <= end <= 2025):
                print("Years must be between 1990 and 2025!")
                continue
            if start > end:
                print("Start year must be less than or equal to end year!")
                continue
            save_search(years)
            query = ("""SELECT title, release_year, description
                              FROM film
                              WHERE release_year BETWEEN %s AND %s""",
                           (start, end))
            result = execute_query(conn, query, (start, end))
        else: # Single year
            if len(years) != 4 or not years.isdigit():
                print("Invalid format! Enter a 4-digit year (YYYY).")
                continue
            year = int(years)
            if not (1990 <= year <= 2025):
                print("Year must be between 1990 and 2025!")
                continue
            save_search(year)
            query = """SELECT title, release_year, description
                              FROM film
                              WHERE release_year = %s"""
            result = execute_query(conn, query, (year,))

        if handle_results(result):
            break

def show_popular_queries():
    """
    Shows top 5 popular queries from MongoDB.
    Has two options: by frequency and by latest.
    return: date formatted as YYYY-MM-DD, time formatted as HH:MM, item
    """
    print("\n------ Top 5 Queries by Frequency ------")
    pipeline = [
        {"$group": {"_id": "$query", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    for item in mongo_collection.aggregate(pipeline):
        print(f"'{item['_id']}' - {item['count']} times")

    print("\n------ Last 5 Queries -------")
    last_queries = mongo_collection.find().sort("datetime", -1).limit(5)
    for item in last_queries:
        print(f"{item['datetime']}: '{item['query']}'")


def main():
    """
    Main function of the program. Asking user to enter search query and show results.
    :return: query results from MySQL database
    """
    conn = get_mysql_connection()
    print("="*50,"\nWelcome to our new Movie Search App!\n" + "="*50)

    while True:
        print("\nWhich movie do you want to search?\n" + "-"*50)
        choice = input("Enter 1 - if you want to find the movie by title or keyword."
                "\nEnter 2 - if you want to find the movie by genre. "
                "\nEnter 3 - if you want to find the movie by year or range of years. "
                "\nEnter 4 - show top 5 popular queries." 
                "\nEnter 5 - if you want to EXIT. "  
                "\n----------------------------------------------"      
                "\nYour Choice: ").strip()
        if choice == "1":
            search_by_title(conn)
        elif choice == "2":
            search_by_genre(conn)
        elif choice == "3":
            search_by_year(conn)
        elif choice == "4":
            show_popular_queries()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Try again.")
    conn.close()
    print("Goodbye!  See you later!")

main()