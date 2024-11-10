import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv 

load_dotenv()

# Define database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

def initialize_tables():
    # Read the SQL file
    with open("createTables.sql", "r") as f:
        create_tables_sql = f.read()
    #print("test1")
    # Connect to the PostgreSQL server
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    #print('test2')
    conn.autocommit = True
    cursor = conn.cursor()

    # Execute the SQL script to create tables if they don't exist
    cursor.execute(create_tables_sql)
    #print("test3")
    cursor.close()
    conn.close()
    print("Tables initialized if they did not already exist.")

# Call initialize_tables when the application starts
if __name__ == "__main__":
    initialize_tables()
