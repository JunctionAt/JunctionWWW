from wtforms import Field

__author__ = 'hansihe'


from flask import render_template


class UserSelectionWidget(object):
    """
    Renders the HTML for the user/player selection widget.
    """

    def __init__(self):
        pass

    def __call__(self, field, **kwargs):
        return render_template("user_selection_widget.html")


class UserSelectionField(Field):
    widget = UserSelectionWidget()

    def process_formdata(self, valuelist):
        super(UserSelectionField, self).process_formdata(valuelist)

    def _value(self):
        pass