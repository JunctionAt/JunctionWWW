from .. import blueprint
from flask import render_template, redirect, url_for
from ..database.threads import Thread
from .. import base36


@blueprint.route("/forum/topic/<string:topic_id>/<topic_name>")
@blueprint.route("/forum/topic/<string:topic_id>/<topic_name>/")
def topic(topic_id, topic_name=None):
    thread = Thread.objects(topic_url_id=base36.decode(topic_id)).first()
    return render_template("forum_posts.html", topic=thread)

@blueprint.route("/forum/topic/<string:topic_id>")
@blueprint.route("/forum/topic/<string:topic_id>/")
def topic_redirect(topic_id):
    thread = Thread.objects(topic_url_id=base36.decode(topic_id)).first()
    return redirect(url_for('forum.topic', topic_id=topic_id, topic_name=thread.topic_url_name))