from pathlib import Path

import flask.json
from mongoengine import BooleanField, Document, ListField, StringField, URLField


class App(Document):
    """
    Model for OAuth applications
    """
    name = StringField(required=True, unique=True)
    short_description = StringField()
    long_description = StringField()
    url = URLField()
    client_id = StringField()
    admin = BooleanField()

    # OAuth Access Token
    redirect_uris = ListField(URLField())
    scopes = ListField(StringField())

    @classmethod
    def admin_app(cls):
        app = cls.objects(admin=True).first()
        if not app:
            data_path = Path(__file__).parent / '../data/admin-app.json'
            with open(data_path) as fp:
                data = flask.json.load(fp)
            app = cls(**data)
            app.save()
        return app
