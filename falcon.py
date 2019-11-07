import os
from flask import Flask 
from plugins.db import db
import datetime


app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello!"


SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]


slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)
sc = SlackClient(SLACK_BOT_TOKEN)

def simple_reply(channel, text):
    sc.api_call("chat.postMessage", channel=channel, text=text)

@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    emoji = event_data["event"]["reaction"]
    print(emoji)


@slack_events_adapter.on("message")
def event_handler(event_data):
    
    # ignore events older than 2s
    delta = datetime.datetime.now().timestamp() - float(event_data["event"]["ts"]) # ts difference
    print("Delta=%f"%delta)

    if event_data["event"].get('subtype') is None and delta < 2:

        m = event_data["event"]["text"]
        c = event_data["event"]["channel"]
        u = event_data["event"]["user"]

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

@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    return

if __name__ == "__main__":
    app.run()
    