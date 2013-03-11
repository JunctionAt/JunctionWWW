__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort
from flask_login import current_user
from blueprints.bans.ban_model import Note
from blueprints.bans.appeal_model import Appeal
from blueprints.auth import login_required
import math

NOTES_PER_PAGE = 10

@bans.route('/a/notes/list/', defaults={'page': 1})
@bans.route('/a/notes/list/<int:page>')
def notes_index(page):
    if not current_user.has_permission('bans.note.view'):
        abort(403)
    if page == 0:
        abort(404)

    notes = Note.objects(active=True).order_by('-time')
    note_num = len(notes)

    num_pages = math.ceil(note_num/float(NOTES_PER_PAGE))
    if num_pages < page:
        if page==1:
            return render_template('no_result_bans.html', message='No notes found.')
        abort(404)

    display_notes = notes.skip((page-1)*NOTES_PER_PAGE).limit(NOTES_PER_PAGE)
    location_info = "Page %i/%i, %i results with %i results per page" % (page, num_pages, note_num, NOTES_PER_PAGE)
    next_button = page < num_pages
    previous_button = page > 1 and not num_pages == 1

    return render_template(
        'notes_index.html',
        view="bans.notes_index",
        notes=display_notes,
        location_info=location_info,
        next_button=next_button,
        previous_button=previous_button,
        current_page=page
    )