#! ../env/bin/python

from flask import Flask
from webassets.loaders import PythonLoader as PythonAssetsLoader
from verifier_app import assets
from verifier_app.models import db
from verifier_app.controllers.main import main
from verifier_app.tasks import start_celery
from verifier_app.extensions import (
    cache,
    assets_env,
    debug_toolbar,
    login_manager,
    celery_client
)


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. verifier_app.settings.ProdConfig
    """

    app = Flask(__name__)

    app.config.from_object(object_name)

    # initialize the cache
    cache.init_app(app)

    # initialize the debug tool bar
    debug_toolbar.init_app(app)

    # initialize SQLAlchemy
    db.init_app(app)

    login_manager.init_app(app)

    # Import and register the different asset bundles
    assets_env.init_app(app)
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().items():
        assets_env.register(name, bundle)

    # register our blueprints
    app.register_blueprint(main)

    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

    celery_client.__init__(main=app.name, broker=app.config['CELERY_BROKER_URL'],
                           backend=app.config['CELERY_RESULT_BACKEND'])
    celery_client.conf.update(app.config)

    start_celery()

    return app
