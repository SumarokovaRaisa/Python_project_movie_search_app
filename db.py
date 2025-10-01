from pymongo import MongoClient
import os
import dotenv
from pathlib import Path
import pymysql


dotenv.load_dotenv(Path('.env'))


# MySQL
MYSQL_HOST = os.environ.get('HOST')
MYSQL_USER = os.environ.get('USER')
MYSQL_PASSWORD = os.environ.get('PASSWORD')
MYSQL_DB = "sakila"

def get_mysql_connection():
    """
    Returns connection to MySQL.
    """
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset="utf8"
    )

# ---------------- MongoDB ----------------
MONGO_URI = os.environ.get('MONGO_URI')
MONGO_DB_NAME = "ich_edit"
MONGO_COLLECTION_NAME = "final_project_250425-ptm_Raisa"

def get_mongo_collection():
    """
    Returns collection MongoDB.
    """
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    print("Connected to MongoDB")

    # Creating collection if not exists
    if MONGO_COLLECTION_NAME not in db.list_collection_names():
        db.create_collection(MONGO_COLLECTION_NAME)

    collection = db[MONGO_COLLECTION_NAME]
    return client, collection


def show_popular_queries():
    """
    Show top 5 popular queries from MongoDB.
    Two options: by frequency and by latest.
    """
    print("\n----- Top 5 Queries by Frequency -----")
    pipeline = [
        {"$group": {"_id": "$query", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    for item in MONGO_COLLECTION_NAME.aggregate(pipeline):
        print(f"'{item['_id']}' - {item['count']} times")

    print("\n------- Last 5 Queries ------")
    last_queries = MONGO_COLLECTION_NAME.find().sort("datetime", -1).limit(5)
    for item in last_queries:
        print(f"{item['datetime']}: '{item['query']}'")
