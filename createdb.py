import sqlite3

conn = sqlite3.connect('database.db')
print ("Opened database successfully")

conn.execute(
    'CREATE TABLE users ( email VARCHAR(255) NOT NULL, password_hash VARCHAR(255) NOT NULL, admin VARCHAR(255) NOT NULL, UNIQUE (email))')
print ("Table created successfully")
conn.close()
