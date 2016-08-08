from flask import (Flask, render_template, request, flash, redirect, session,
                   url_for)
from flask_pymongo import PyMongo, DESCENDING
from flask_pagedown import PageDown
from flask_misaka import Misaka
from flask_wtf.csrf import CsrfProtect

from forms import PostForm

from bson.objectid import ObjectId

import bcrypt

import datetime

app = Flask(__name__)
app.config.from_object('config')

csrf = CsrfProtect(app)
mongo = PyMongo(app)
pagedown = PageDown(app)
misaka = Misaka(app)


@app.route('/')
def index():
    # New posts first
    posts = list(mongo.db.posts.find().sort('created', DESCENDING))
    return render_template('index.html',
                           posts=posts)


@app.route('/imprint')
def imprint():
    return render_template('imprint.html')


@app.route('/addpost', methods=['GET', 'POST'])
def addpost():
    if not session.get('logged_in'):
        return redirect('/')
    form = PostForm()
    if request.method == 'POST' and form.validate_on_submit():
        post = mongo.db.posts
        # Check for updating post
        if session.get('post_id') is not None:
            post.update_one({'_id': ObjectId(session['post_id'])},
                            {'$set': {'headline': form.headline.data,
                                      'content': form.content.data,
                                      'author': form.author.data,
                                      'modified':
                                      datetime.datetime.now()}})
            session['post_id'] = None
        else:
            post.insert({'headline': form.headline.data,
                         'content': form.content.data,
                         'author': form.author.data,
                         'created': datetime.datetime.now()})
        return redirect('/')
    elif session.get('post_id') is not None:
        cur_post = mongo.db.posts.find_one({'_id': ObjectId(
                                            session['post_id'])})
        form.headline.data = cur_post['headline']
        form.content.data = cur_post['content']
        form.author.data = cur_post['author']
    flash(form.errors)
    return render_template('addpost.html',
                           form=form)


@app.route('/delete_entry/<post_id>', methods=['POST'])
def delete_entry(post_id):
    mongo.db.posts.delete_one({'_id': ObjectId(post_id)})
    return redirect('/')


@app.route('/update_entry/<post_id>', methods=['POST'])
def update_entry(post_id):
    if request.method == 'POST':
        session['post_id'] = post_id
        return redirect(url_for('addpost'))
    return redirect('/')


@app.route('/anmelden', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Generating username/password once
        # users = mongo.db.users
        # hashed_pw = bcrypt.hashpw(request.form['password'].encode('utf-8'),
        #                           bcrypt.gensalt())
        # users.insert({'name': request.form['username'],
        #               'password': hashed_pw})
        user = mongo.db.users.find_one({'name': request.form['username']})
        if user:
            if bcrypt.hashpw(
                request.form['password'].encode('utf-8'),
                    user['password']) == user['password']:
                    session['logged_in'] = True
                    return redirect('/')
        return 'Falsche Benutzername/Passwort-Kombination'

    return render_template('anmelden.html')


@app.route('/logout')
def logout():
    session['logged_in'] = None
    return redirect('/')


@app.route('/add')
def add():
    user = mongo.db.users
    user.insert({'name': 'Timon'})
    return 'Added User!'


if __name__ == '__main__':
    app.run(debug=True)
