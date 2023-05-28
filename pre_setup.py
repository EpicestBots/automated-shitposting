import sqlite3
import os

if not os.path.exists('database'):
    os.mkdir('database')

posts = sqlite3.connect('database/posts.db')
print("Opened database successfully")

posts.execute(
    '''CREATE TABLE posts
	(ID INTEGER PRIMARY KEY     AUTOINCREMENT,
	LINK         TEXT    NOT NULL,
	REDDIT_ID    TEXT    NOT NULL,
	DATE         TEXT    NOT NULL,
	MEDIA        TEXT    NOT NULL
);'''
)

print("Table created successfully")

posts.close()
