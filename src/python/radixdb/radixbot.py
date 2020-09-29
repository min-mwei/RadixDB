from flask import Flask, jsonify, send_file, request, url_for, Response
from slackeventsapi import SlackEventAdapter
from slack import WebClient
import os
import sys
import asyncio
import asyncpg
import radixdb.executor
import radixdb.evaluator
import os
import io
import json
import uuid
import base64
from jinja2 import Template
from pathlib import Path

async def create_pool():
    return await asyncpg.create_pool(database='radixdb', user='postgres', port=5432)

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
pool = loop.run_until_complete(create_pool())
config = radixdb.executor.run_query(loop, pool,
                                    """select hstore_merge(hstore(name, value))::hstore kv from tokens where context = 'bot1'""")
slack_client = WebClient(config['slack_bot_token'])
slack_events_adapter = SlackEventAdapter(config['slack_signing_secret'], "/slack/events", app)

def exec_query(sql):
    return radixdb.executor.exec_query(loop, pool, sql)

root = str(Path(__file__).parent) + '/web/'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def radix_home(path):
    print("load path:", path)
    if path.endswith(".js"):
        print("path:", path)
        return send_file(root+path, mimetype="text/javascript")
    elif path.endswith(".css"):
        return send_file(root+path, mimetype="text/css")
    elif path.endswith(".png"):
        return send_file(root+path, mimetype="image/png")
    return send_file(root+'index.html', mimetype="text/html")

@app.route('/query', methods=['POST'])
def execute_query():
    length = request.headers["Content-Length"]
    print("len:", length)
    bytes = io.BytesIO(request.get_data())
    code = io.TextIOWrapper(bytes, encoding='utf-8')
    q =code.read().strip()
    print("q:", q)
    ret=radixdb.evaluator.radixdb_eval(q)
    if len(ret) > 1:
        packet = {'text': ret[0].head(10).to_html(), 'plot': ret[1]}
    else:
        packet = {'text': ret[0].head(10).to_html()}
    return Response(json.dumps(packet), status=200, mimetype='application/json')

def get_single_vaue(query):
    values = radixdb.executor.run_query(loop, pool, query)
    return values[0][0]

history = {}

#get_image?name=
@app.route('/get_image')
def get_image():
    #sql = """SELECT  data from contents where name='%s' limit 1; """ % request.args.get('name')
    #print("sql:", sql)
    #value = radixdb.executor.run_query(loop, pool, sql)
    k = request.args.get('name')
    try :
        print("get image", k)
        print("sql:", "select data from contents where name ='{0}';".format(k))
        ret = exec_query("select data from contents where name ='{0}';".format(k))
        if len(ret):
            #print("ret:", type(ret[0]), ret[0]['data'])
            buf = base64.b64decode( ret[0]['data'][len("data:image/png;base64,"):])
            return send_file(
                io.BytesIO(buf),
                mimetype='image/png',
                attachment_filename='%s.png' % request.args.get('name'))
    except Exception as e:
        print(e)

    return Response(json.dumps({"oops": "hmm"}), status=200, mimetype='application/json')

@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

# Create an event listener for "reaction_added" events and print the emoji name
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    emoji = event_data["event"]["reaction"]
    print(emoji)

@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    #print("event_data", event_data)
    message = event_data["event"]
    if message['client_msg_id'] in history:
        print("already seen this")
        return
    history[message['client_msg_id']] = 0
    print("got:", message)
    channel = message["channel"]
    cmd = message['text']
    if cmd != '':
        q = cmd[cmd.find(' ')+1:].strip()
        print("query:", q)
        ret=radixdb.evaluator.radixdb_eval(q, plot_encoding=False)
        #message = "Hello <@{0}>! :tada: here is the result:{1}".format(message["user"], str(ret))
        img_url = ""
        if len(ret) > 1:
            k = str(uuid.uuid4())
            print("insert into database")
            radixdb.executor.do_insert_value(loop, pool, k, ret[1])
            img_url =config['public_image_url'] + "/get_image?name=" + k
            print("img_url:", img_url)
        res = None
        try:
            res = slack_client.api_call("chat.postMessage", json={'channel': channel,
                                                              "blocks":json.dumps([
                                                                  {
                                                                      "type": "section",
                                                                      "text": {
                                                                          "type": "mrkdwn",
                                                                        "text": ret[0].head(10).to_markdown()
                                                                      }
                                                                  },
                                                                  {
                                                                      "type": "image",
                                                                      "title": {
                                                                          "type": "plain_text",
                                                                          "text": "a diagram"
                                                                      },
                                                                      "block_id": "image1",
                                                                      "image_url": img_url,
                                                                      "alt_text": "Blash"
                                                                  }
                                                              ])})
        except Exception as e:
            print("xxxxxx:", e)
        print("res:", res)

#insert into tokens values ('bot1', 'public_image_url', 'https://6d3aec56.ngrok.io');
#gunicorn --bind 0.0.0.0:3000 radixdb.radixbot:app
#gunicorn --bind 0.0.0.0:3000 radixdb.radixbot:app -w 4 --threads 12 --worker-connections 1000
# Start the server on port 3000

if __name__ == "__main__":
    app.run(port=3000, debug=True)
