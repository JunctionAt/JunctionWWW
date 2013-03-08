__author__ = 'HansiHE'

from flask import render_template, jsonify, request, current_app, abort, flash, redirect, url_for

from blueprints.api import apidoc
from blueprints.player_groups.group_model import Group

from blueprints.player_groups import player_groups

@apidoc(__name__, player_groups, '/<server>/group/<group>.json', endpoint='show_group', defaults=dict(ext='json'))
def show_group_api(server, group, ext):
    """Show info for ``group``.

    Returns an object with its primary key being the value of ``group``. Eg.:

    .. code-block::

       {
           "Techs": {
               "display_name": "Techs",
               "tagline": "Do you need halp?",
               "link": "junction.at",
               "info": "Currently documenting the API...",
               "public": 0
           }
       }

    *Note:* Blank fields in ``group`` will be omitted from the object.
    """

def show_group(server, group, ext):
    try:
        self = player_groups[server]
    except KeyError:
        abort(404)
    name = group
    #group = session.query(Group).filter(Group.id.in_([
    #    "%s.%s"%(self.server,name),
    #    "%s.pending.%s"%(self.server,name)
    #])).one()
    group = Group.objects(gid__in=[
        "%s.%s"%(self.server,name),
        "%s.pending.%s"%(self.server,name)
    ]).first()
    if group is None:
        abort(404)
    if not group.name == name:
        # Redirect to preferred caps
        return redirect(url_for('player_groups.show_group', server=self.server, group=group.name, ext=ext)), 301
    if ext == 'json':
        g = dict(display_name=group.display_name)
        if group.tagline: g['tagline']=group.tagline
        if group.link: g['link']=group.link
        if group.info: g['info']=group.info
        if group.public: g['public']=group.public
        return jsonify({group.name:g})
    return render_template('show_group.html', endpoint=self, group=group)