__author__ = 'HansiHE'

import flask
from flask import Blueprint, url_for, render_template, jsonify, current_app, abort
from blueprints.base import cache
import markdown
from markdown.inlinepatterns import Pattern
from markdown.extensions import Extension
import requests
import json
import re
import reddit_wiki_comp

blueprint = Blueprint('wiki', __name__,
    template_folder='templates')

wiki_markdown = markdown.Markdown()

INTERNAL_LINK_PATTERN = r'(?<=\()\/r\/.unction\/wiki\/.*?(?=\))'
REDDIT_LINK_PATTERN = r'(?<=\()\/.*?(?=\))'

reddit_headers = {
    'User-Agent': "junction.at/wiki by HansiHE"
}

def replace_internal_link(match):
    return match.group(0).split('/', 4)[4]

def replace_reddit_link(match):
    return 'http://reddit.com'+match.group(0)

class RedditSucksException(Exception): pass

@cache.memoize(timeout=20*60)
def get_wiki_article(wiki_url):
    try:
        api_request = requests.get('http://api.reddit.com/r/Junction/wiki/%s' % wiki_url, timeout=3, headers=reddit_headers)
    except requests.RequestException, e:
        raise RedditSucksException(e.__class__.__name__ + ": " + e.message)

    if api_request.status_code != 200:
        raise RedditSucksException("request returned with code " + str(api_request.status_code) + ", not 200")

    json_data = api_request.json()
    content = json_data['data']['content_md']

    content = re.sub(INTERNAL_LINK_PATTERN, replace_internal_link, content)
    content = re.sub(REDDIT_LINK_PATTERN, replace_reddit_link, content)
    content = content.replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<')

    return {'content': content, 'title': ""}

@cache.memoize(timeout=20*60)
def get_wiki_pages():
    try:
        api_request = requests.get('http://api.reddit.com/r/Junction/wiki/pages/', timeout=3, headers=reddit_headers)
    except requests.RequestException, e:
        raise RedditSucksException(e.__class__.__name__ + ": " + e.message)

    if api_request.status_code != 200:
        raise RedditSucksException("request returned with code " + str(api_request.status_code) + ", not 200")

    json_data = api_request.json()
    pages = json_data['data']
    pages = filter(lambda page: page.find('/')==-1 and not page.startswith('_'), pages)

    return pages

@blueprint.route('/wiki/pages/')
def display_pages():
    try:
        return render_template('wiki_listing.html', links=get_wiki_pages(), title="All Pages - Wiki")
    except RedditSucksException, e:
        cache.delete_memoized(get_wiki_pages)
        return render_template('reddit_down.html', title="reddit is down - Wiki", message=e.message)

@blueprint.route('/wiki/')
def display_index():
    try:
        return render_template('wiki_page.html', article=get_wiki_article('index'), index=True, title="Wiki")
    except RedditSucksException, e:
        cache.delete_memoized(get_wiki_article, 'index')
        return render_template('reddit_down.html', title="reddit is down - Wiki", message=e.message)

@blueprint.route('/wiki/<string:wiki_url>')
def display_wiki_article(wiki_url):
    try:
        return render_template('wiki_page.html', article=get_wiki_article(wiki_url), index=False, wiki_url=wiki_url, title=wiki_url + " - Wiki")
    except KeyError:
        abort(404)
    except RedditSucksException, e:
        cache.delete_memoized(get_wiki_article, wiki_url)
        return render_template('reddit_down.html', title="reddit is down - Wiki", message=e.message)
