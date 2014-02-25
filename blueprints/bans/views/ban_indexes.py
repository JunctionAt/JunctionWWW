__author__ = 'HansiHE'

from .. import bans
from flask import render_template, abort, url_for
from flask_login import current_user
from blueprints.bans.ban_model import Ban, Note
from blueprints.auth import login_required
from blueprints.auth.util import require_permissions
import math


class Index(object):

    def __init__(self, model, func_name, title, no_results_message, no_results_template, results_template, call_decorator=lambda f: f):
        self.model = model
        self.__name__ = func_name
        self.endpoint_name = "." + func_name
        self.title = title
        self.no_results_message = no_results_message

        self.no_results_template = no_results_template
        self.results_template = results_template

        self.query = {}
        self.order_by = []

        self.call = call_decorator(self.call)

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def call(self, page):
        if page == 0:
            abort(404)

        iter_query = dict()
        for key, value in self.query.iteritems():
            if hasattr(value, '__call__'):
                iter_query[key] = value()
            else:
                iter_query[key] = value

        appeals = self.model.objects(**iter_query).order_by(*self.order_by)
        appeal_num = len(appeals)
        num_pages = int(math.ceil(appeal_num / float(BANS_PER_PAGE)))
        if num_pages < page:
            if page==1:
                return render_template(self.no_results_template, message=self.no_results_message, view=self.endpoint_name, title=self.title)
            abort(404)

        display_appeals = appeals.skip((page - 1) * BANS_PER_PAGE).limit(BANS_PER_PAGE)

        next_page = url_for(self.endpoint_name, page=page+1) if page < num_pages \
            else None
        prev_page = url_for(self.endpoint_name, page=page-1) if page > 1 and not num_pages == 1 \
            else None

        links = []
        for page_mod in range(-min(PAGINATION_VALUE_RANGE, page - 1), min(PAGINATION_VALUE_RANGE, num_pages-page) + 1):
            num = page + page_mod
            links.append({'num': num, 'url': url_for(self.endpoint_name, page=num), 'active': num != page})

        return render_template(
            self.results_template,
            view=self.endpoint_name,
            base_title=self.title,
            objects=display_appeals,
            total_pages=num_pages,
            next=next_page,
            prev=prev_page,
            links=links
        )


BANS_PER_PAGE = 15
PAGINATION_VALUE_RANGE = 3

your_bans = Index(Ban, 'your_bans', "Your bans", "You have no bans.", 'no_result_bans.html', 'bans_index.html')
your_bans.query = {"username": lambda: current_user.name}
your_bans.order_by = ['-time']

bans.add_url_rule('/a/bans/your/', 'your_bans', your_bans, defaults={'page': 1})
bans.add_url_rule('/a/bans/your/<int:page>', 'your_bans', your_bans)


created_bans = Index(Ban, 'created_bans', "Bans you've made", "No bans found.", 'no_result_bans.html', 'bans_index.html')
created_bans.query = {"issuer": lambda: current_user.name}
created_bans.order_by = ['-time']

bans.add_url_rule('/a/bans/created/', 'created_bans', created_bans, defaults={'page': 1})
bans.add_url_rule('/a/bans/created/<int:page>', 'created_bans', created_bans)


bans_index = Index(Ban, 'bans_index', "All Bans", "No bans found.", 'no_result_bans.html', 'bans_index.html')
bans_index.query = {"active": True}
bans_index.order_by = ['-time']

bans.add_url_rule('/a/bans/list/', 'bans_index', bans_index, defaults={'page': 1})
bans.add_url_rule('/a/bans/list/<int:page>', 'bans_index', bans_index)


notes_index = Index(Note, 'notes_index', "All Notes", "No notes found.", 'no_result_bans.html', 'notes_index.html', require_permissions('bans.create'))
notes_index.query = {"active": True}
notes_index.order_by = ['-time']

bans.add_url_rule('/a/notes/list', 'notes_index', notes_index, defaults={'page': 1})
bans.add_url_rule('/a/notes/list/<int:page>', 'notes_index', notes_index)


appeals_index = Index(Ban, 'appeals_index', "All Appeals", "No appeals found.", 'no_result_bans.html', 'appeals_index.html')
appeals_index.query = {"__raw__": {"appeal.replies.0": {"$exists": 1}}}
appeals_index.order_by = ['-appeal.last']

bans.add_url_rule('/a/appeals/list', 'appeals_index', appeals_index, defaults={'page': 1})
bans.add_url_rule('/a/appeals/list/<int:page>', 'appeals_index', appeals_index)