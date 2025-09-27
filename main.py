from db import get_mysql_connection, get_mongo_collection
from utils import paginate_results, select_genre
from datetime import datetime

genres = ['Action', 'Animation', 'Children', 'Classics', 'Comedy', 'Documentary',
          'Drama', 'Family', 'Foreign', 'Games', 'Horror', 'Music',
          'Sci-Fi', 'Sports', 'Travel', 'New']

mongo_collection = get_mongo_collection()


def save_search(query):
    """Saving result in MongoDB"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    mongo_collection.insert_one({"query": query, "datetime": now})


def display_results(results, page_size=10):
    """
    Displays results page by page with continuous numbering.
    Asks the user 'Show more?' only if the page is full.
    """
    counter = 1
    for page in paginate_results(results, page_size):
        for row in page:
            print(f"{counter}. {row[0]} ({row[1]}),\nDescription: '{row[2]}'")
            counter += 1
        if len(page) < page_size:
            break
        if input("Show more? (y/n): ").lower() != "y":
            break


def search_by_title(conn):
    title = input("Enter movie title or keyword: ")
    save_search(title)
    with conn.cursor() as cursor:
        cursor.execute("""SELECT title, release_year,description
                          FROM film 
                          WHERE title LIKE %s""",
                          ("%" + title + "%",))
        result = cursor.fetchall()

    if not result:
        print("No movies found.")
        return
    display_results(result)


def search_by_genre(conn):
    genre = select_genre(genres)
    save_search(genre)
    with conn.cursor() as cursor:
        sql = """SELECT f.title, f.release_year, c.name, f.description
                 FROM film f
                 JOIN film_category fc ON fc.film_id = f.film_id
                 JOIN category c ON fc.category_id = c.category_id
                 WHERE LOWER(c.name) = LOWER(%s)"""
        cursor.execute(sql, (genre,))
        result = cursor.fetchall()

    if not result:
        print("No movies found. Try again.")
        return
    display_results(result)


def search_by_year(conn):
    while True:
        years = input("Enter a year or range (e.g. 2006-2008) from 1990 to 2025: ").strip()
        with conn.cursor() as cursor:
            if "-" in years:
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
                cursor.execute("""SELECT title, release_year, description
                                  FROM film
                                  WHERE release_year BETWEEN %s AND %s""",
                               (start, end))
            else:
                if len(years) != 4 or not years.isdigit():
                    print("Invalid format! Enter a 4-digit year (YYYY).")
                    continue
                year = int(years)
                save_search(year)
                cursor.execute("""SELECT title, release_year, description
                                  FROM film
                                  WHERE release_year = %s""", (year,))

            result = cursor.fetchall()

            if not result:
                print("No movies found. Try again.")
                continue
            break
    display_results(result)

def show_popular_queries():
    """
    Show top 5 popular queries from MongoDB.
    Two options: by frequency and by latest.
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
    conn = get_mysql_connection()
    print("_"*50,"\nWelcome to our new Movie Search App!\n" + "_"*50)

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