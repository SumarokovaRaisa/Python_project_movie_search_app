#  Movie Search App
------------------------------------------------
##  Project Goal
Create an interactive **console application** for searching movies in the
`sakila` (MySQL) database with the following features:
------------------------------------------------
##  Features
### 1. Search for Movies
- **By keyword**
  - Search by movie title
  - Results are limited to **10 movies per page**
  - The user can request the **next 10 results** until there are no more
- **By genre and release year range**
  - Before entering input, the user is shown:
    - A **list of all genres** from the database
    - The **minimum and maximum release year** of movies in the database
  - The user specifies:
    - A **year range** (e.g., `2005-2012`)
    - Or a **specific year**
  - Results are displayed **10 movies at a time** with user-controlled pagination
--------------------------------------------------
### 2. Save Search History
All user search queries are stored in **MongoDB** in the collection:
--------------------------------------------------
### 3. Popular Queries
The application displays a list of the **top 5 popular queries**,
based on:
- **Frequency** (most common searches), or
- **Recent searches**
----------------------------------------------------
##  Technologies Used
- **Python 3**
- **MySQL** (sakila database)
- **MongoDB** (for saving search history)
- **pymysql**, **pymongo**
------------------------------------------------------
##  How to Run
```bash
python main.py
-------------------------------------------------------


"""Цель проекта
Создать интерактивное консольное приложение для поиска фильмов по базе
данных sakila (MySQL) с возможностью:
1. Искать фильмы:
○ По ключевому слову
■ Поиск по названию фильма
■ Результат ограничен 10 фильмами
■ По запросу пользователя отображаются следующие 10 результатов, или
пока не закончатся
○ По жанру и диапазону годов выпуска
■ Перед вводом пользователю показываются:
■ Список всех жанров из таблицы жанров
■ Минимальный и максимальный год выпуска фильмов в базе
■ Указывается нижняя и верхняя граница, например: от 2005 до 2012, или
конкретный год
■ По запросу пользователя отображаются следующие 10 результатов, или
пока не закончатся
2. Сохранять все поисковые запросы в MongoDB в коллекцию
final_project_<your_group>_<your_full_name>.
3. Выводить список из 5 популярных запросов (по частоте или последним
поискам)"""
----------------------------------
