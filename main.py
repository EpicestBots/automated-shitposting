from utils import get_top_post, add_post_to_blacklist
from pprint import pprint
from urllib.request import urlretrieve
import sqlite3
import os
import tweepy
from datetime import datetime
import random
import shutil
from munch import DefaultMunch
import schedule
import time
from dotenv import load_dotenv


def get_random_troll_word():
    with open('database/troll_words.txt', 'r', encoding="utf-8") as file:
        words_list = file.read().split('\n')

    return random.choice(words_list)


def cleanup():
    print("Resetting media folder")
    shutil.rmtree('media')
    os.mkdir('media')


def get_message(post_id):
    conn = sqlite3.connect('database/posts.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM posts")
    count = cursor.fetchone()[0]
    conn.close()
    return f"Shitpost #{count+1} with a minuscule amount of {get_random_troll_word()}"


def add_post_to_database(status, post):
    conn = sqlite3.connect('database/posts.db')
    cursor = conn.cursor()
    reddit_id = post["id"]
    location = post["location"]
    cursor.execute(
        f"INSERT INTO posts (LINK, REDDIT_ID, DATE, MEDIA) VALUES ('https://twitter.com/shitposting_bot/status/{status.id}', '{reddit_id}', '{datetime.now()}', '{location}')")
    conn.commit()
    print(f"Added post with id [{reddit_id}] to database")
    conn.close()


def post_on_twitter(post):
    load_dotenv()
    CONSUMER_KEY = os.getenv("CONSUMER_KEY")
    CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuth1UserHandler(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)

    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    if (post["type"] == "video"):
        media_category = "tweet_video"
    elif (post["url"].endswith("gif")):
        media_category = "tweet_gif"
    else:
        media_category = "tweet_image"

    media = api.media_upload(
        post["location"], media_category=media_category, chunked=True, wait_for_async_finalize=True)

    status = client.create_tweet(text=get_message(
        post["id"]), media_ids=[media.media_id_string]).data
    status = DefaultMunch.fromDict(status)
    print(
        f"Posted on twitter at: https://twitter.com/shitposting_bot/status/{status.id}")
    add_post_to_database(status, post)


def get_subreddit_names():
    with open('database/subreddits.txt', 'r') as file:
        return "+".join(file.read().split('\n'))


def check_if_post_exists(post_id):
    posts = sqlite3.connect('database/posts.db')
    cursor = posts.cursor()
    cursor.execute(f"SELECT * FROM posts WHERE REDDIT_ID = '{post_id}'")
    return cursor.fetchone() is not None


def sanitize_extension(filename):
    extension = filename.split('.')[-1].split('?')[0]
    print(f"File Extension: {extension}")
    return extension


def process_post(post):
    dash = "-"*(len(post['title'])+7)
    print(f"Posting content from https://reddit.com{post['permalink']}")
    print(dash)
    print(f"Title: {post['title']}")
    print(f"Link: https://reddit.com{post['permalink']}")
    print(f"Media: {post['url']}")
    print(f"Score: {post['score']}")
    print(dash)
    filename = ""
    if not os.path.exists('media'):
        os.mkdir('media')
    if (post["url"].startswith("https://v.redd.it")):
        filename = f"media/{post['id']}.mp4"
        media = post["media"]
        post["type"] = "video"
    else:
        filename = f"media/{post['id']}.{sanitize_extension(post['url'])}"
        media = post["url"]
        post["type"] = "image"
    urlretrieve(media, filename)
    post["location"] = filename
    post_on_twitter(post)


def main():
    current_post = {"id": -1}
    try:
        posts = get_top_post(get_subreddit_names())
        while True:
            current_post = posts.pop(0)
            if check_if_post_exists(current_post["id"]) == False:
                break
            else:
                print(
                    f"Post with id [{current_post['id']}] already exists, choosing another one")
        process_post(current_post)
    except Exception as error:
        print("An error occured:")
        print(error)
        print("Adding to blacklist and trying again in 30 minutes")
        if current_post["id"] != -1:
            add_post_to_blacklist(current_post["id"])
        else:
            print("[CRITICAL ERROR] No post was processed, skipping blacklist")


if __name__ == '__main__':
    schedule.every(30).minutes.do(main).run()
    schedule.every().day.at("00:00").do(cleanup)

    while True:
        schedule.run_pending()
        time.sleep(1)
    # main()
