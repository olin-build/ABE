from pathlib import Path
from uuid import uuid4

import flask.json
from mongoengine import Document, ListField, StringField, URLField

BUILTIN_APPS_PATH = Path(__file__).parent / f'../data/builtin-apps.json'


class App(Document):
    """
    Model for OAuth applications
    """
    name = StringField(required=True, unique=True)
    short_description = StringField()
    long_description = StringField()
    url = URLField()
    client_id = StringField()

    # OAuth
    redirect_uris = ListField(URLField())
    scopes = ListField(StringField())

    # builtins
    role = StringField()
    redirect_prefixes = ListField(StringField())  # non-URL prefixes for builtins

    @classmethod
    def admin_app(cls):
        return cls.force_client(role='admin')

    @classmethod
    def force_client(cls, role):
        app = cls.objects(role=role).first()
        if not app:
            with open(BUILTIN_APPS_PATH) as fp:
                apps_data = flask.json.load(fp)
            data = next(d for d in apps_data if d['role'] == role)
            data['client_id'] = uuid4().hex
            app = cls(**data)
            app.save()
        return app

    def validate_redirect_uri(self, redirect_uri):
        redirect_uris = self.redirect_uris + self.redirect_prefixes
        return any(redirect_uri.startswith(uri) for uri in redirect_uris)
