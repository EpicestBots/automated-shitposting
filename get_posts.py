import os
import praw
from dotenv import load_dotenv
import requests

load_dotenv()


def convert_bytes(num):
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return f"{num:.2f} {x}"
        num /= 1024.0


def get_file_size(url):
    return int(requests.head(url, timeout=30).headers["Content-Length"])


def get_top_post(subreddit) -> dict:
    reddit = praw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        password=os.getenv("PASSWORD"),
        user_agent="testscript by u/yt-reddit",
        username=os.getenv("USERNAME"),
    )
    posts = []
    for submission in reddit.subreddit(subreddit).top(time_filter="day", limit=30):
        opts = {}
        if (not submission.over_18 and not submission.pinned and not submission.is_video):
            file_size = get_file_size(submission.url)
            if file_size > 5 * 1024 * 1024:
                preview_file = submission.preview['images'][0]['source']['url']
                print(
                    f"File too large ({convert_bytes(file_size)}), using preview instead with size {convert_bytes(get_file_size(preview_file))}")
                opts["url"] = preview_file
            else:
                opts["url"] = submission.url
            opts["title"] = submission.title
            opts["permalink"] = submission.permalink
            opts["id"] = submission.id
            opts["media"] = submission.media["reddit_video"]["fallback_url"] if submission.media else None
            opts["score"] = submission.score
            posts.append(opts)
    return posts
