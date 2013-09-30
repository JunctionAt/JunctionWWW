__author__ = 'HansiHE'

from flask import current_app
import praw
from .. import blueprint


reddit_oauth = praw.Reddit('https://Junction.at reddit OAuth | /u/JunctionBot subreddit flair bot')
reddit_oauth.login('JunctionBot', '^pOd9$qHU&t8J#t8Nd#m')
reddit_oauth.set_oauth_app_info(current_app.config["REDDIT_CLIENT_ID"], current_app.config["REDDIT_CLIENT_SECRET"],
                                current_app.config["REDDIT_REDIRECT_URL"])
subreddit = current_app.config["REDDIT_SUBREDDIT"]


def get_flair(reddit_user):
    for flair_item in reddit_oauth.get_subreddit(subreddit).get_flair_list():
        if flair_item['user'] == reddit_user:
            flair = flair_item['flair_text']
            return flair

