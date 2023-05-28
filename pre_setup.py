import sqlite3
import os

if not os.path.exists('database'):
    os.mkdir('database')

if not os.path.exists('database/posts.db'):
    posts = sqlite3.connect('database/posts.db')
    print("Opened database posts successfully")

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

if not os.path.exists('database/blacklist.db'):
    blacklist = sqlite3.connect('database/blacklist.db')
    print("Opened database blacklist successfully")

    blacklist.execute(
        '''CREATE TABLE blacklist
		(ID INTEGER PRIMARY KEY     AUTOINCREMENT,
		REDDIT_ID    TEXT    NOT NULL
	);'''
    )

    print("Table created successfully")

    blacklist.close()
