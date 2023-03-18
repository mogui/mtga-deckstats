import json
from .stats import convert_deck, get_stats

from flask import (
    Blueprint, flash,  render_template, request
)




bp = Blueprint('main', __name__)
@bp.route('/', methods=('GET', 'POST'))
def main():
    data = {}
    if request.method == 'POST':
        deck_str = request.form['deck']
        error = None
        if not deck_str:
            error = 'Insert exported deck.'

        if error is None:
            conv = convert_deck(deck_str)
            stats = get_stats(conv)
            data['converted_deck'] = conv
            data['stats'] = stats
        else:
            flash(error)
            
    return render_template('main.html', data=data)