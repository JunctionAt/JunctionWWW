__author__ = 'HansiHE'

from .. import blueprint
from flask import render_template, request, redirect, url_for, abort
from ..database.forum import Forum, Category, Board, Topic

@blueprint.route('/forum/b/<int:board_id>/')
def view_board_redirect(board_id):
    board = Board.objects(board_id=board_id).first()
    if board is None:
        abort(404)
    return redirect(url_for('forum.view_board', board_id=board_id, board_name=board.name.replace(' ', '_'), page=1))

@blueprint.route('/forum/b/<int:board_id>/<string:board_name>/', defaults={'page': 1})
@blueprint.route('/forum/b/<int:board_id>/<string:board_name>/page/<int:page>/')
def view_board(board_id, board_name, page):
    board = Board.objects(board_id=board_id).first()
    if board is None:
        abort(404)
    if not board_name == board.get_url_name():
        return redirect(board.get_url())
    forum = board.forum

    topics = Topic.objects(board=board)

    return render_template('forum_board.html', board=board, forum=forum, topics=topics)