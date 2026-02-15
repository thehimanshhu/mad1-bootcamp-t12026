from flask import current_app as app

@app.route("/hello")
def index():
    return "hello"
