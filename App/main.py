import os
from flask import Flask, render_template
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from App.database import init_db
from App.config import load_config
from App.controllers import setup_jwt, add_auth_context
from App.views import views, setup_admin
from App.views.map import map_views
from App.controllers.marker import marker_views
from flask_login import LoginManager
from App.models.user import User

def add_views(app):
    for view in views:
        app.register_blueprint(view)

def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)
    add_auth_context(app)

    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)

    add_views(app)  # auth_views is already included here via __init__.py
    app.register_blueprint(map_views)
    app.register_blueprint(marker_views)

    init_db(app)
    jwt = setup_jwt(app)
    setup_admin(app)

    login_manager = LoginManager()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.init_app(app)
    login_manager.login_view = 'auth_views.login'


    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    def custom_unauthorized_response(error):
        return render_template('401.html', error=error), 401

    app.app_context().push()
    return app
