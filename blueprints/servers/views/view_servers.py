__author__ = 'williammck'

from flask import render_template, send_file, abort
import StringIO

from .. import blueprint
from models.servers_model import Server


@blueprint.route('/servers/')
def view_servers():
    servers = Server.objects()
    return render_template('servers_view_servers.html', servers=servers, title="Servers")

@blueprint.route('/servers/<string:server_id>.png')
def view_server_image(server_id):
    server = Server.objects(server_id=server_id).first()
    if server is None:
        abort(404)

    image = StringIO.StringIO(server.server_image.read())
    image.seek(0)
    return send_file(image, mimetype='image/png')
