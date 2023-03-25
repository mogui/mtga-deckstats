import os

from flask import Flask


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    from . import main
    app.register_blueprint(main.bp)
    
    from . import stats
    stats.init_app(app)

    return app