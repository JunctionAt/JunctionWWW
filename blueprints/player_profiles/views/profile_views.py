from flask import render_template, abort, request, redirect
from flask_wtf import Form
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Length

from .. import blueprint
from models.user_model import User
from models.forum_model import Post, Topic
from models.profile_model import PlayerProfile
from ..badges import render_badges
from .admin_reset import ResetForm
from blueprints.auth import current_user, login_required


@blueprint.route('/p/<string:name>/')
def profile_view(name):
    user = User.objects(name=name).first()
    if user is None:
        abort(404)

    forum_info = ForumInfo(user)

    profile = get_profile(user)

    reset_form = ResetForm()

    return render_template('profile_view.html', user=user, forum_info=forum_info, profile=profile, render_badges=render_badges, title="{} - Profile".format(user.name), reset_form=reset_form)


class ProfileTextEditForm(Form):
    text = TextAreaField("Profile text", validators=[
        Length(min=0, max=5000, message="The profile text needs to be below 5000 characters.")])
    submit = SubmitField("Submit")


@blueprint.route('/p/<string:name>/edit/', methods=['GET', 'POST'])
@login_required
def profile_text_edit(name):
    if current_user.name != name:
        abort(404)
    profile = get_profile(current_user)
    form = ProfileTextEditForm(request.form)

    if request.method == 'POST':
        if not form.validate():
            return render_template('profile_edit_text.html', profile=profile, form=form)

        profile.profile_text = form.text.data
        profile.save()
        return redirect(current_user.get_profile_url())

    form.text.data = profile.profile_text
    return render_template('profile_edit_text.html', profile=profile, form=form, user=current_user, title="Edit Profile - " + name + " - Profile")


class ForumInfo(object):
    def __init__(self, user):
        posts_raw = Post.objects(author=user.to_dbref()).order_by('-date')
        self.post_num = len(posts_raw)
        self.forum_activity = posts_raw.limit(6)
        self.topic_num = len(Topic.objects(author=user))


def get_profile(user):
    profile = PlayerProfile.objects(user=user.to_dbref()).first()
    if profile is None:
        profile = PlayerProfile(user=user.to_dbref())
        profile.save()
    return profile
