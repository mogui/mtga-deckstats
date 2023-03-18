import os

from flask import Flask


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.environ.get('DATABASE', './db/mtga.db'),
    )

    from . import mtgdb
    from . import main
    app.register_blueprint(main.bp)
    mtgdb.init_app(app)
    
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app