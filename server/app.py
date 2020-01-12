import os
from flask import Flask, Response

app = Flask(__name__)


@app.route("/")
def index():
    content = open(os.path.join(os.path.dirname("__file__"), "feed.xml"))
    return Response(content, mimetype="text/xml")


app.run()
