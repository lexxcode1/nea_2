# import mysql.connector
# from mysql.connector.abstracts import MySQLConnectionAbstract
# from mysql.connector.pooling import PooledMySQLConnection

from config import config

# def connect() -> PooledMySQLConnection | MySQLConnectionAbstract:
#     """
#     Connects to the database and returns the connection object
#
#     :returns: MySQLConnection | MySQLConnectionPool : Connection object
#     """
#     try:
#         return mysql.connector.connect(**config)
#     except mysql.connector.Error as err:
#         print("Failed to connect to database:", err)
#         exit()  # Terminate if connection fails


import sqlite3


def connect() -> sqlite3.Connection:
    return sqlite3.connect("nea.db")
