__author__ = 'HansiHE'

from flask import Blueprint, request, render_template, abort, send_file, flash, redirect, url_for
from blueprints.auth import login_required

admin = Blueprint('admin', __name__, template_folder='templates')