from .. import blueprint
from flask import render_template
from ..database.threads import Thread

@blueprint.route("/forum/topic/<topic_uuid>/")
def topic(topic_uuid):
    thread = Thread.objects(topic_uuid=topic_uuid).first()
    return render_template("forum_posts.html", topic=thread)
