from .. import blueprint
from ..database.boards import Board
from ..database.categories import Category
from flask import render_template

@blueprint.route("/forum/board/<board_id>/")
def forum_category(board_id):
    board = Board.objects(board_id=board_id).first()
    categories = Category.objects
    category = [category for category in categories if board in category.boards][0]
    return render_template("forum_board.html", category=category, board=board, topics=board.topics)
