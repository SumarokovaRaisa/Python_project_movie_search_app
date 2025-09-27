def paginate_results(results, page_size=10):
    """Генерирует результаты постранично"""
    total = len(results)
    for i in range(0, total, page_size):
        yield results[i:i + page_size]

def select_genre(genres):
    """Выбор жанра пользователем по номеру"""
    print("Available genres:")
    for i, g in enumerate(genres, start=1):
        print(f"{i}. {g}")

    while True:
        try:
            num = int(input("Enter the number of your genre: "))
            if 1 <= num <= len(genres):
                return genres[num - 1]
            print(f"Enter a number between 1 and {len(genres)}.")
        except ValueError:
            print("Invalid input! Enter a number.")

# def show_popular_queries():
#     """
#     Show top 5 popular queries from MongoDB.
#     Two options: by frequency and by latest.
#     """
#     print("\n--- Top 5 Queries by Frequency ---")
#     pipeline = [
#         {"$group": {"_id": "$query", "count": {"$sum": 1}}},
#         {"$sort": {"count": -1}},
#         {"$limit": 5}
#     ]
    # for item in mongo_collection.aggregate(pipeline):
    #     print(f"'{item['_id']}' - {item['count']} times")
    #
    # print("\n--- Last 5 Queries ---")
    # last_queries = mongo_collection.find().sort("datetime", -1).limit(5)
    # for item in last_queries:
    #     print(f"{item['datetime']}: '{item['query']}'")