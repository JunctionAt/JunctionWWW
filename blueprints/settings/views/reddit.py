__author__ = 'HansiHE'

from flask import render_template, request, url_for, flash, redirect
from blueprints.base import csrf
from blueprints.auth import current_user, login_required
import praw, md5, os
from .. import blueprint
from . import add_settings_pane, settings_panels_structure

#DO NOT USE CURRENT_APP - there's some problem here with it infinitely recursing.

CLIENT_ID = 'YfYyXm8wPjag2w'
CLIENT_SECRET = '3pFHaT9xDyjRC2ZBnmjl3kusavE'
REDIRECT_URI = 'https://williammck-dev.junction.at/settings/reddit/link'

#subreddit = current_app.config.get('REDDIT_SUBREDDIT')
subreddit = 'Junction'

reddit_oauth = praw.Reddit('https://Junction.at reddit OAuth | /u/JunctionBot subreddit flair bot')
#reddit_oauth.set_oauth_app_info(current_app.config.get('REDDIT_CLIENT_ID'), current_app.config.get('REDDIT_CLIENT_SECRET'),
#                                current_app.config.get('REDDIT_REDIRECT_URI'))
reddit_oauth.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

def get_flair(reddit_username):
    for flair_item in reddit_oauth.get_subreddit(subreddit).get_flair_list():
        if flair_item['user'] == reddit_username:
            flair = flair_item['flair_text']
            return flair

@blueprint.route('/settings/reddit')
@login_required
def reddit_pane():
    reddit_username = current_user.reddit_username
    flair = get_flair(current_user.reddit_username)
    return render_template('settings_reddit.html', current_user=current_user,
                            reddit_username=reddit_username,
                            flair=flair,
                            settings_panels_structure=settings_panels_structure,
                            title="Settings - Account - Reddit")

@blueprint.route('/settings/reddit/link', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def reddit_link():
    if request.method == 'POST':
        state = md5.new(os.urandom(24)).hexdigest()
        link = reddit_oauth.get_authorize_url(state, 'identity')
        return redirect("%s" % link)
    try:
        reddit_oauth.get_access_information(request.args.get('code', ''))
        reddit_username = reddit_oauth.get_me().name
        current_user.reddit_username = reddit_username
        current_user.save()
        flash('Reddit username successfully linked.')
        return redirect(url_for('settings.reddit_pane'))
    except:
        flash('Unable to link your username. Did you make sure to click accept?')
        return redirect(url_for('settings.reddit_pane'))

@blueprint.route('/settings/reddit/unlink', methods=['POST'])
@login_required
@csrf.exempt
def reddit_unlink():
    reddit_username = current_user.reddit_username
    if reddit_username != None:
        if get_flair(reddit_username) != None:
            reddit_oauth.get_subreddit(subreddit).set_flair(reddit_username)
            flash('Your flair has been unset on /r/%s.' % subreddit)
        current_user.reddit_username = None
        current_user.save()
        flash('Reddit username successfully unlinked.')
        return redirect(url_for('settings.reddit_pane'))
    else:
        flash('You must have a username linked to do that.')
        return redirect(url_for('settings.reddit_pane'))

@blueprint.route('/settings/reddit/set_flair', methods=['POST'])
@login_required
@csrf.exempt
def reddit_set_flair():
    username = current_user.name
    reddit_username = current_user.reddit_username
    if reddit_username != None:
        if username.lower() != reddit_username.lower():
            reddit_oauth.login('JunctionBot', '^pOd9$qHU&t8J#t8Nd#m')
            reddit_oauth.get_subreddit(subreddit).set_flair(reddit_username, username)
            flash('Your flair has been set on /r/%s.' % subreddit)
            return redirect(url_for('settings.reddit_pane'))
        else:
            flash('Your usernames are the same, so no flair is needed.')
            return redirect(url_for('settings.reddit_pane'))
    else:
        flash('You must have a username linked to do that.')
        return redirect(url_for('settings.reddit_pane'))

@blueprint.route('/settings/reddit/unset_flair', methods=['POST'])
@login_required
@csrf.exempt
def reddit_unset_flair():
    reddit_username = current_user.reddit_username
    if reddit_username != None:
        reddit_oauth.login('JunctionBot', '^pOd9$qHU&t8J#t8Nd#m')
        reddit_oauth.get_subreddit(subreddit).set_flair(reddit_username)
        flash('Your flair has been unset on /r/%s.' % subreddit)
        return redirect(url_for('settings.reddit_pane'))
    else:
        flash('You must have a username linked to do that.')
        return redirect(url_for('settings.reddit_pane'))

add_settings_pane(lambda: url_for('settings.reddit_pane'), "Account", "Reddit")
