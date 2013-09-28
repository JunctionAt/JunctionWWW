__author__ = 'HansiHE'

from flask import url_for, render_template, request, redirect, abort, flash
from blueprints.settings.views import add_settings_pane, settings_panels_structure
from .. import blueprint
from blueprints.auth import login_required, current_user
from ..apikey_model import ApiKey
from wtforms import Form, TextField, StringField, SelectMultipleField
from wtforms.validators import Length

@blueprint.route('/settings/api')
@login_required
def api_key_settings_pane():
    keys = ApiKey.objects(owner=current_user.to_dbref())
    return render_template('api_settings_pane.html', settings_panels_structure=settings_panels_structure, keys=keys)


class AddApiKeyForm(Form):
    label = TextField("Label", validators=[Length(max=20)], default="no label")


@blueprint.route('/settings/api/addkey', methods=["POST"])
@login_required
def api_key_add():
    form = AddApiKeyForm(request.form)

    key = ApiKey(owner=current_user.to_dbref(), label=form.label.data)
    key.save()

    flash("Key has been added.")

    return redirect(url_for('api.api_key_edit', key_id=key.id))


@blueprint.route('/settings/api/delkey/<string:key_id>', methods=["POST"])
@login_required
def api_key_delete(key_id):
    key = ApiKey.objects(id=key_id).first()
    if key is None or current_user != key.owner:
        abort(401)

    key.delete()
    flash("Key has been deleted.")

    return redirect(url_for('api.api_key_settings_pane'))


class PreSelectMultipleField(SelectMultipleField):
    pass


class ApiKeyEditForm(Form):
    label = StringField("Label")
    acl = PreSelectMultipleField("ACL", choices=[("testval", "Test"), ("testval2", "Test 2")])


@blueprint.route('/settings/api/key/<string:key_id>/')
@login_required
def api_key_edit(key_id):
    key = ApiKey.objects(id=key_id).first()
    if key is None or current_user != key.owner:
        abort(401)

    form = ApiKeyEditForm()

    form.label.data = key.label
    form.acl.data = ['testval']

    return render_template('api_settings_edit_pane.html', settings_panels_structure=settings_panels_structure, form=form, key=key)

add_settings_pane(lambda: url_for('api.api_key_settings_pane'), "Developer", "Api Keys", menu_id="api_keys")