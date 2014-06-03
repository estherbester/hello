# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2014 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


# create our little application :)
app = Flask(__name__,  static_url_path='')

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'attendees.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""

    with app.app_context():
            db = get_db()
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()


def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select id, name, why, fun from entries order by id asc')
    entries = cur.fetchall()
    return render_template('render.html', entries=entries)

@app.route('/new')
def new():
    db = get_db()
    cur = db.execute('select name, why, fun from entries order by id desc')
    entries = cur.fetchall()
    return render_template('new.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    #if not session.get('logged_in'):
    #    abort(401)
    db = get_db()
    cursor = db.cursor()
    cursor.execute('insert into entries (name, why, fun) values (?, ?, ?)',
               [request.form['name'], request.form['why'], request.form['fun']])
    flash('New person added! ID:%s' % cursor.lastrowid)
    db.commit()
    return redirect(url_for('new'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == "__main__":
    app.run(port=8085, host='0.0.0.0')
