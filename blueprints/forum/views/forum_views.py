__author__ = 'HansiHE'

from flask import render_template, redirect, url_for, abort

from .. import blueprint
from ..database.forum import Forum, Category, Topic


@blueprint.route('/forum/')
def forum_landing():
    return redirect(url_for('forum.view_forum', forum='main'))

@blueprint.route('/forum/f/<string:forum>/')
def view_forum(forum):
    forum = Forum.objects(identifier=forum).first()
    if forum is None:
        abort(404)
    categories = Category.objects(forum=forum)
    recent_topics = Topic.objects(forum=forum).order_by('-date').limit(5)

    return render_template("forum_index.html", categories=categories, forum=forum, recent_topics=recent_topics)

#@blueprint.route('/f/a/s/')
#def setup():
#    category = Category.objects.first()
#    forum = Forum.objects(identifier="main").first()
#    board = Board()
#    board.name = "General Chat"
#    board.forum = forum
#    board.categories = [category]
#    board.description = "Put chatter here pls"
#    board.save()
#    return 'yes'