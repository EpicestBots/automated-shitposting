import os
import praw
from dotenv import load_dotenv
import requests
import sqlite3

load_dotenv()

MAX_FILE_SIZE = 15 * 1024 * 1024  # 5MB


def add_post_to_blacklist(post_id):
    conn = sqlite3.connect('database/blacklist.db')
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO blacklist (REDDIT_ID) VALUES ('{post_id}')")
    conn.commit()
    print(f"Added post with id [{str(post_id)}] to blacklist")
    conn.close()


def convert_bytes(num):
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return f"{num:.2f} {x}"
        num /= 1024.0


def check_if_blacklisted(post_id):
    blacklist = sqlite3.connect('database/blacklist.db')
    cursor = blacklist.cursor()
    cursor.execute(f"SELECT * FROM blacklist WHERE REDDIT_ID = '{post_id}'")
    return cursor.fetchone() is not None


def get_file_size(url):
    try:
        return int(requests.head(url, timeout=30).headers["Content-Length"])
    except KeyError:
        print(
            f"Content-Length header not found for {url}. Using content.__sizeof__()")
        return requests.get(url, timeout=30).content.__sizeof__()


def post_type(submission):
    if getattr(submission, 'post_hint', '') == 'image':
        return 'image'
    elif getattr(submission, 'is_gallery', False):
        return 'gallery'
    elif submission.is_video:
        return 'video'
    elif hasattr(submission, 'poll_data'):
        return 'poll'
    elif hasattr(submission, 'crosspost_parent'):
        return 'crosspost'
    elif submission.is_self:
        return 'text'
    return 'link'


def get_top_post(subreddit) -> dict:
    reddit = praw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        password=os.getenv("PASSWORD"),
        user_agent="testscript by u/yt-reddit",
        username=os.getenv("USERNAME"),
    )
    posts = []
    for submission in reddit.subreddit(subreddit).top(time_filter="day", limit=42):
        opts = {}
        if (not submission.over_18 and not submission.pinned and not submission.is_video and post_type(submission) in ["image", "video"] and not check_if_blacklisted(submission.id)):
            file_size = get_file_size(submission.url)
            if file_size > MAX_FILE_SIZE:
                print(
                    f"Skipping {submission.url} because it's too large ({convert_bytes(file_size)} and adding it to blacklist")
                add_post_to_blacklist(submission.id)
                continue
            opts["url"] = submission.url
            opts["title"] = submission.title
            opts["permalink"] = submission.permalink
            opts["id"] = submission.id
            opts["media"] = submission.media["reddit_video"]["fallback_url"] if submission.media else None
            opts["score"] = submission.score
            posts.append(opts)
    return posts
