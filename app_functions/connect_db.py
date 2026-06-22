import os
from dotenv import load_dotenv
from pymongo import MongoClient


def connect_db(database: str):
    print("Connecting to the Mongo database...")

    load_dotenv()

    connection_string = os.getenv("MONGO_CONNECTION_STRING")

    if not connection_string: raise RuntimeError("The Mongo Connection String was not found.")

    client = MongoClient(connection_string)

    if not client: raise RuntimeError("Client is None.")

    db = client[database]

    print("Connected to the Mongo database")

    return db
