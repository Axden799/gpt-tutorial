from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from gpt_chat_app.db import get_db

from flask import current_app

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

async def generate_reply(query, agent_group):
    #client = OpenAI()
    #completion = client.chat.completions.create(
    #    model="gpt-3.5-turbo",
    #    messages=[
    #        {"role": "system", "content": "You are a bread maker's assistant, capable of recalling recipes about different types of bread.#"},
    #        {"role": "user", "content": query}
    #    ]
    #)
    #chat_result = agent_group.user_proxy.initiate_chat(
    #    agent_group.assistant,
    #    message=query,
    #)
    chat_result = agent_group.generate_reply(query)

    print("I EXITED YESSSS")
    print(chat_result)
    #return completion.choices[0].message.content
    return chat_result

@bp.route('/', methods=['GET'])
def index():
    db = get_db()

    messages = get_messages(db)
    return render_template('base.html', messages=messages)

@bp.route('/chat', methods=['POST'])
async def submit_query():
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
        code_generator = current_app.config['CODE_GEN']
        reply = await generate_reply(query, code_generator)
        #post message to db
        post_message(db, reply, 1)
        print(reply)
        # Redirect to a GET request after processing the form
        
    return redirect(url_for('chat.index'))
