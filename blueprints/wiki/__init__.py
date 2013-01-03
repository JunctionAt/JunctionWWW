__author__ = 'HansiHE'

import flask
from flask import Blueprint, url_for, render_template, jsonify, current_app
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
#wiki_markdown.registerExtension(reddit_wiki_comp.makeExtension())

#IMAGE_PATTERN = r''
INTERNAL_LINK_PATTERN = r'(?<=\()\/r\/.unction\/wiki\/.*?(?=\))'
REDDIT_LINK_PATTERN = r'(?<=\()\/.*?(?=\))'
#LINK_PATTERN = re.compile(r'.*')
#class RedditImageProcessor(Pattern):
#    def run(self, text):
#        return text

#class RedditLinkProcessor(Pattern):
#    def handleMatch(self, m):
#        print 'ma'
#        return 'match'

#wiki_markdown.inlinePatterns['reddit_link_processor'] = RedditLinkProcessor(LINK_PATTERN, wiki_markdown)

#class RedditSyntaxExtension(Extension):
#    def extendMarkdown(self, md, md_globals):
#        #md.postprocessors.add('reddit_image_processor', RedditImageProcessor(IMAGE_PATTERN), '_end')
#
#        print 'mm'

#wiki_markdown.registerExtension(RedditSyntaxExtension())

#@cache.cached(timeout=20*60, key_prefix='pic_bindings')
#@cache.memoize(timeout=20*60)
#def get_pic_bindings():
#    result = requests.get('http://api.reddit.com/r/Junction/wiki/_picrefs').json['data']['content_md']
#    result = result.split('\n', 1)[1].replace("\r", "").replace("\n", "")
#    print result
#    return json.loads(result)

@cache.memoize(timeout=20*60)
def get_wiki_article(wiki_url):
    def replace_internal_link(match):
        return match.group(0).split('/', 4)[4]
    def replace_reddit_link(match):
        return 'http://reddit.com'+match.group(0)
    api_request = requests.get('http://api.reddit.com/r/Junction/wiki/%s' % wiki_url)
    json = api_request.json
    if json.has_key('reason'):
        return json['reason']
    #get_pic_bindings()
    content = json['data']['content_md']
    #Hackish, for now
    #print re.match(LINK_PATTERN, content)
    content = re.sub(INTERNAL_LINK_PATTERN, replace_internal_link, content)
    content = re.sub(REDDIT_LINK_PATTERN, replace_reddit_link, content)
    return wiki_markdown.convert(content)

@cache.cached(timeout=20*60)
@blueprint.route('/wiki/pages/')
def display_pages():
    pages = requests.get('http://api.reddit.com/r/Junction/wiki/pages/').json['data']
    pages = filter(lambda page: page.find('/')==-1 and not page.startswith('_'), pages)
    return render_template('wiki_listing.html', links=pages)

@blueprint.route('/wiki/')
def display_index():
    return render_template('wiki_page.html', article=get_wiki_article('index'), index=True)

@blueprint.route('/wiki/<string:wiki_url>')
def display_wiki_article(wiki_url):
    return render_template('wiki_page.html', article=get_wiki_article(wiki_url), index=False)