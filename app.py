from flask import Flask
from application.models import db
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite3"
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()

from application.routes import *

if __name__ =="__main__":
    app.run()