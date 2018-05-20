from pathlib import Path

import flask.json
from mongoengine import Document, ListField, StringField, URLField


class App(Document):
    """
    Model for OAuth applications
    """
    name = StringField(required=True, unique=True)
    short_description = StringField()
    long_description = StringField()
    url = URLField()
    client_id = StringField()
    role = StringField()

    # OAuth Access Token
    redirect_uris = ListField(URLField())
    scopes = ListField(StringField())

    @classmethod
    def admin_app(cls):
        return cls.force_client(role='admin')

    @classmethod
    def force_client(cls, role):
        app = cls.objects(role=role).first()
        if not app:
            data_path = Path(__file__).parent / f'../data/{role}-app.json'
            with open(data_path) as fp:
                data = flask.json.load(fp)
            app = cls(**data)
            app.save()
        return app

    def validate_redirect_uri(self, redirect_uri):
        redirect_uris = self.redirect_uris
        if self.role == 'admin':
            redirect_uris += ['/']
        if self.role == 'fallback':
            redirect_uris += ['/', 'http://', 'https://']
        return any(redirect_uri.startswith(uri) for uri in redirect_uris)
