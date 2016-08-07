from flask import (Flask, render_template, request, flash, redirect, session,
                   url_for)
from flask_pymongo import PyMongo, DESCENDING
from flask_pagedown import PageDown
from flask_misaka import Misaka
from flask_wtf.csrf import CsrfProtect

from forms import PostForm

from bson.objectid import ObjectId

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
    # old_post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
    # return redirect(url_for('addpost', old_post=old_post))
    # return redirect('/')


@app.route('/add')
def add():
    user = mongo.db.users
    user.insert({'name': 'Timon'})
    return 'Added User!'


if __name__ == '__main__':
    app.run(debug=True)
