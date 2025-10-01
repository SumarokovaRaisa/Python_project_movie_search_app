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


def validate_years(years, genre=None):
    """
    Validate year input (single year or range) and build SQL query.
    :param years: input string (YYYY or YYYY-YYYY)
    :param genre: optional movie genre; if provided, query filters by genre
    :return: tuple (query, params) or None if input is invalid
    """
    if "-" in years: # Проверка диапазона лет
        parts = years.split("-")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            print("Invalid format! Use YYYY-YYYY.")
            return None
        start, end = map(int, parts)
        if not (1990 <= start <= 2025 and 1990 <= end <= 2025):
            print("Years must be between 1990 and 2025!")
            return None
        if start > end:
            print("Start year must be less than or equal to end year!")
            return None

        save_search(f"{genre + ', ' if genre else ''}{years}")

        if genre:
            query = """SELECT f.title, f.release_year, c.name, f.description
                       FROM film f
                                JOIN film_category fc ON fc.film_id = f.film_id
                                JOIN category c ON fc.category_id = c.category_id
                       WHERE LOWER(c.name) = LOWER(%s)
                         AND f.release_year BETWEEN %s AND %s"""
            params = (genre, start, end)
        else:
            query = """SELECT title, release_year, description
                       FROM film
                       WHERE release_year BETWEEN %s AND %s"""
            params = (start, end)
        return query, params

    else:   # Проверка одного года
        if len(years) != 4 or not years.isdigit():
            print("Invalid format! Enter a 4-digit year (YYYY).")
            return None
        year = int(years)
        if not (1990 <= year <= 2025):
            print("Year must be between 1990 and 2025!")
            return None

        save_search(f"{genre + ', ' if genre else ''}{year}")

        if genre:
            query = """SELECT f.title, f.release_year, c.name, f.description
                       FROM film f
                                JOIN film_category fc ON fc.film_id = f.film_id
                                JOIN category c ON fc.category_id = c.category_id
                       WHERE LOWER(c.name) = LOWER(%s)
                         AND f.release_year = %s"""
            params = (genre, year)
        else:
            query = """SELECT title, release_year, description
                       FROM film
                       WHERE release_year = %s"""
            params = (year,)

        return query, params

def search_by_genre_and_year(conn):
    """
    Search movies by genre AND year (or year range).
    Both genre and year are required.
    :param conn: MySQL connection
    """
    genre = select_genre(genres) # Обязательный выбор жанра

    while True:
        # Ввод года или диапазона лет
        years = input("Enter a year or range (e.g. 2006-2008) from 1990 to 2025: ").strip()

        validated = validate_years(years, genre) # Валидация и подготовка запроса
        if not validated:
            continue  # если ввод некорректный, повторяем

        query, params = validated
        result = execute_query(conn, query, params) # Выполнение запроса

        if handle_results(result): # Обработка результатов
            break

def search_by_year(conn):
    """
    Searching movie by year or range of years (1990 - 2025), using format YYYY-YYYY
    :param conn: MySQL connection
    :return: movie title, year of release, genre and description
    """
    while True:
        years = input("Enter a year or range (e.g. 2006-2008) from 1990 to 2025: ").strip()
        validated = validate_years(years)
        if not validated:
            continue  # если ввод некорректный, повторяем
        query, params = validated
        result = execute_query(conn, query, params)

        if handle_results(result):
            break

def show_last_queries():
    """
    Shows last 5 search queries from MongoDB.
    return: date formatted as YYYY-MM-DD, time formatted as HH:MM, item
    """
    print("\n------ Last 5 Queries ------")
    last_queries = mongo_collection.find().sort("datetime", -1).limit(5)
    for item in last_queries:
        print(f"{item['datetime']} - '{item['query']}'")


def show_top_5_queries():
    """
    Shows last 5 search queries from MongoDB.
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
                "\nEnter 4 - if you want to find the movie by genre and year or range of years. "                   
                "\nEnter 5 - show top 5 popular queries." 
                "\nEnter 6 - show 5 latest queries." 
                "\nEnter 7 - if you want to EXIT. "  
                "\n----------------------------------------------"      
                "\nYour Choice: ").strip()
        if choice == "1":
            search_by_title(conn)
        elif choice == "2":
            search_by_genre(conn)
        elif choice == "3":
            search_by_year(conn)
        elif choice == "4":
            search_by_genre_and_year(conn)
        elif choice == "5":
            show_top_5_queries()
        elif choice == "6":
            show_last_queries()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Try again.")
    conn.close()
    print("Goodbye!  See you later!")

main()