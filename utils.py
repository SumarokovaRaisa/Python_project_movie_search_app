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

