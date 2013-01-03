from .. import blueprint
import time
from flask_login import current_user
from blueprints.auth import login_required
import shortuuid
from ..database.boards import Board
from ..database.threads import Thread
from ..database.posts import Post
from ..database.counters import Counter
from flask import render_template, request, redirect, url_for, abort
from .. import base36

@blueprint.route("/forum/reply/<string:topic_id>", methods=["POST","GET"])
@login_required
def reply(topic_id):
    if request.method == "POST":
        body = request.form.get("reply", False)
        if body:
            topic = Thread.objects(topic_url_id=base36.decode(topic_id)).first()
            post = Post(author=current_user.name,content=body)
            post.save()
            topic.posts.append(post)
            topic.save()
            return render_template("forum_success.html", topic_id=topic_id, topic_name=topic.topic_url_name)
        return render_template("forum_failiure.html", topic_id=topic_id)
    else:
        # First validate to see its a valid topic_id, if its not then 404 that son of a bitch.
        valid = Thread.objects(topic_id=base36.decode(topic_id)) != []
        if not valid:
            abort(404)
        return render_template("forum_reply.html")

@blueprint.route("/forum/new_topic/<string:board_name>", methods=["POST","GET"])
@login_required
def new_topic(board_name):
    if request.method == "GET":
        return render_template("forum_new_topic.html")
    else:
        # get the board
        board = Board.objects(name=board_name).first()
        # Get the title and body from the POST
        title = request.form.get("title")
        body = request.form.get("reply")

        # Get the database reference'd author
        author = current_user.name

        date = time.asctime()

        safe_name = str(title).lower()
        safe_name = safe_name.replace(" ", "-")
        safe_name = filter(str.isalnum, safe_name)

        # Construct and save the thread
        thread = Thread(title=title, author=author, topic_url_name=safe_name, date=date)
        thread.save()
        # Construct and save the post.
        first_post = Post(author=author, content=body)
        first_post.save()

        thread.posts.append(first_post)
        board.topics.insert(0, thread)
        # Update collections !
        board.save()
        thread.save()

        return render_template("forum_success.html", topic_id=base36.encode(thread.topic_url_id), topic_name=safe_name)
