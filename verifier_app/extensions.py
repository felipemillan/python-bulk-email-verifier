from flask.ext.cache import Cache
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask.ext.login import LoginManager
from flask_assets import Environment
from celery import Celery
from verifier_app.models import User

# Setup flask cache
cache = Cache()

# init flask assets
assets_env = Environment()

debug_toolbar = DebugToolbarExtension()

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"

celery_client = Celery()

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)
