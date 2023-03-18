import click
from flask import current_app, g
from mtgtools.MtgDB import MtgDB, PCardList

def get_mtgdb():
    if 'mtgdb' not in g:
        g.mtgdb:MtgDB = MtgDB(current_app.config['DATABASE'])
    return g.mtgdb

def init_db():
    mtgdb = get_mtgdb()
    mtgdb.scryfall_bulk_update()

def close_db(e=None):
    db = g.pop('mtgdb', None)

    if db is not None:
        db.close()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
    
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)