from dotenv import load_dotenv
import os
from flask import Flask 
from flask import request, jsonify
from plugins.db import db
from rocketchat.api import RocketChatAPI
import datetime

# make sure we read the .env file
load_dotenv(verbose=True)
ROCKET_CHAT_DOMAIN=os.getenv("ROCKET_CHAT_DOMAIN")
ROCKET_CHAT_USERNAME=os.getenv("ROCKET_CHAT_USERNAME")
ROCKET_CHAT_PASSWORD=os.getenv("ROCKET_CHAT_PASSWORD")

# establish API link
api = RocketChatAPI(settings={
    'username': ROCKET_CHAT_USERNAME,
    'password': ROCKET_CHAT_PASSWORD,
    'domain': ROCKET_CHAT_DOMAIN
})

app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello!"


@app.route("/falcon/api/message", methods=['POST'])
def process_request():
    req = {
        'who': request.json['user_name'],
        'text': request.json['text'],
        'bot': bool(request.json['bot']),
        'channel': request.json['channel_id']
    }
    print(req)
    event_handler(req)
    return 'OK', 200

def simple_reply(channel, message):
    api.send_message(message, channel)

def event_handler(event):
    m = event['text']
    c = event['channel']
    u = event['who']
    print(m,c,u)
    # simple_reply(c,"test")

    m = m.split(' ')

    # retrieve definition
    if m[0] == '??' and len(m[1]) > 0:
        query = m[1]
        d = db.Database()
        r = d.lookup(query)
        if len(r) == 0:
            simple_reply(c, "Not found")
        else:
            for i in range(0,len(r)):
                simple_reply(c,r[i][0])

    # retrieve preformatted definition
    elif m[0] == '``' and len(m[1]) > 0:
        query = m[1]
        d = db.Database()
        r = d.lookup(query)
        if len(r) == 0:
            simple_reply(c, "Not found")
        else:
            for i in range(0,len(r)):
                simple_reply(c,"```"+r[i][0]+"```")

    # add definition
    elif m[0] == '++' and len(m[1]) > 0 and len(m[2])>0:
        term = m[1]
        definition = ' '.join(m[2:])
        d = db.Database()
        d.add_term(u, term, definition)
        simple_reply(c, "Added %s." % term)

    # remove term (ALL definitions)
    elif m[0] == '--' and len(m[1]) > 0:
        term = m[1]
        d = db.Database()
        r = d.lookup(term)
        if len(r) > 0:
            d.remove_term(term)
            simple_reply(c, "%d entries for %s removed." % (len(r), term))
        else:
            simple_reply(c, "Not found.")


if __name__ == "__main__":
    app.run()
    