from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from gpt_chat_app.db import get_db

from openai import OpenAI

import asyncio

bp = Blueprint('chat', __name__)

messages = []

def get_messages(db):
    messages = db.execute(
        'SELECT * FROM chat'
    ).fetchall()
    return messages

def post_message(db, message, reply=0):
    print(message)
    db.execute(
        'INSERT INTO chat (message, reply)'
        ' VALUES (?, ?)',
        (message, reply)
    )
    db.commit()

def generate_reply(query):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a bread maker's assistant, capable of recalling recipes about different types of bread."},
            {"role": "user", "content": query}
        ]
    )

    return completion.choices[0].message.content

@bp.route('/', methods=('GET', 'POST'))
def index():
    #messages.append(['My first message', 'My second message'])
    if request.method == 'POST':
        db = get_db()
        query = request.form['query']
        error = None

        if not query:
            error = 'Query required'
        
        if error is not None:
            flash(error)
        else:
            post_message(db, query, 0)
            #generate bot reply
            reply = generate_reply(query)
            #post message to db
            post_message(db, reply, 1)

    messages = get_messages(db)
    return render_template('base.html', messages=messages)
