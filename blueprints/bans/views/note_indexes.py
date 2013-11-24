__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort, url_for
from flask_login import current_user
from blueprints.bans.ban_model import Note
from blueprints.bans.appeal_model import Appeal
from blueprints.auth import login_required
from blueprints.auth.util import require_permissions
import math

NOTES_PER_PAGE = 15
PAGINATION_VALUE_RANGE = 3

@bans.route('/a/notes/list/', defaults={'page': 1})
@bans.route('/a/notes/list/<int:page>')
@require_permissions('bans.note.view')
def notes_index(page):

    if page == 0:
        abort(404)

    notes = Note.objects(active=True).order_by('-time')
    note_num = len(notes)

    num_pages = int(math.ceil(note_num / float(NOTES_PER_PAGE)))
    if num_pages < page:
        if page==1:
            return render_template('no_result_bans.html', message="No notes found.", view="bans.notes_index", title="All notes")
        abort(404)

    display_notes = notes.skip( (page-1) * NOTES_PER_PAGE).limit(NOTES_PER_PAGE)
    # Find the links we want for the next/prev buttons if applicable.
    next_page = url_for('bans.notes_index', page=page + 1) if page < num_pages \
        else None
    prev_page = url_for('bans.notes_index', page=page - 1) if page > 1 and not num_pages == 1 \
        else None

    # Mash together a list of what pages we want linked to in the pagination bar.
    links = []
    for page_mod in range(-min(PAGINATION_VALUE_RANGE, page - 1), min(PAGINATION_VALUE_RANGE, num_pages-page) + 1):
        num = page + page_mod
        links.append({'num': num, 'url': url_for('bans.notes_index', page=num), 'active': (num == page)})

    return render_template(
        'notes_index.html',
        view="bans.notes_index",
        base_title="All notes",
        notes=display_notes,
        total_pages=num_pages,
        next=next_page,
        prev=prev_page,
        links=links
    )
