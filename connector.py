import sqlite3


def connect() -> sqlite3.Connection:
    # Connect to the db in the top level file
    return sqlite3.connect("./nea.db")



