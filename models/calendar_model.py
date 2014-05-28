from mongoengine import Document, ReferenceField, StringField, DateTimeField, BooleanField


class Calendar(Document):

    name = StringField(required=True)
    identifier = StringField(required=True)

    meta = {
        'collection': 'calendar_calendar',
        'indexed': []
    }


class Event(Document):

    title = StringField(required=True)

    start = DateTimeField(required=True)
    end = DateTimeField()
    all_day = BooleanField(default=True)

    calendar = ReferenceField(Calendar, dbref=False, required=True)

    htmlClass = StringField()
    color = StringField(default="#3a87ad")
    backgroundColor = StringField()
    borderColor = StringField()
    textColor = StringField(default="#fff")

    meta = {
        'collection': 'calendar_event',
        'indexed': []
    }