__author__ = 'HansiHE'

from flask import url_for, render_template, request, redirect, abort, flash
from blueprints.settings.views import add_settings_pane, settings_panels_structure
from .. import blueprint
from blueprints.auth import login_required, current_user
from ..apikey_model import ApiKey
from flask_wtf import Form
from wtforms import TextField, StringField, SelectMultipleField, SubmitField
from wtforms.validators import Length
from .. import access_tokens

@blueprint.route('/settings/api')
@login_required
def api_key_settings_pane():
    apikey_add_form = AddApiKeyForm(request.form)
    apikey_del_form = DelApiKeyForm(request.form)
    keys = ApiKey.objects(owner=current_user.to_dbref())
    return render_template('api_settings_pane.html', settings_panels_structure=settings_panels_structure, keys=keys, apikey_add_form=apikey_add_form, apikey_del_form=apikey_del_form, title="Settings - Developer - API Keys")


class AddApiKeyForm(Form):
    label = TextField("Label", validators=[Length(max=20)], default="no label")


@blueprint.route('/settings/api/addkey', methods=["POST"])
@login_required
def api_key_add():
    form = AddApiKeyForm(request.form)

    key = ApiKey(owner=current_user.to_dbref(), label=form.label.data)
    key.save()

    flash("Key has been added.", category="success")

    return redirect(url_for('api.api_key_edit', key_id=key.id))


class DelApiKeyForm(Form):
    pass


@blueprint.route('/settings/api/delkey/<string:key_id>', methods=["POST"])
@login_required
def api_key_delete(key_id):
    key = ApiKey.objects(id=key_id).first()
    if key is None or current_user != key.owner:
        abort(401)

    key.delete()
    flash("Key has been deleted.", category="success")

    return redirect(url_for('api.api_key_settings_pane'))


class PreSelectMultipleField(SelectMultipleField):
    pass


class ApiKeyEditForm(Form):
    label = StringField("Label")
    acl = PreSelectMultipleField("ACL")
    submit = SubmitField("Save")


@blueprint.route('/settings/api/key/<string:key_id>/', methods=["GET", "POST"])
@login_required
def api_key_edit(key_id):
    key = ApiKey.objects(id=key_id).first()
    if key is None or current_user != key.owner:
        abort(401)

    form = ApiKeyEditForm()
    form.acl.choices = list()
    for access_token in access_tokens.values():
        if access_token.get("permission"):
            if not current_user.has_permission(access_token.get("permission")):
                continue
        form.acl.choices.append((access_token.get("token"), access_token.get("token")))

    if request.method == "GET":
        form.label.data = key.label
        form.acl.data = key.access

        return render_template('api_settings_edit_pane.html', settings_panels_structure=settings_panels_structure, form=form, key=key, title="Settings - Developer - API Keys - Edit")
    elif request.method == "POST":
        form.validate()

        key.label = form.label.data
        key.access = form.acl.data
        key.save()

        return redirect(url_for('api.api_key_edit', key_id=key_id))

add_settings_pane(lambda: url_for('api.api_key_settings_pane'), "Developer", "API Keys", menu_id="api_keys")
