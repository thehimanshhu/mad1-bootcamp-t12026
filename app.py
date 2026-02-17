from flask import Flask
from application.models import db , Admin , Customer , Professional , Package , Booking
from datetime import datetime
from flask_login import LoginManager
def create_app():
    app = Flask(__name__ , )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite3"
    app.config["SECRET_KEY"] = "mysecretkey"
    db.init_app(app)
    login_manager = LoginManager(app)
    @login_manager.user_loader
    def load_user(email):
        user= db.session.query(Customer).filter_by(email=email).first() or \
        db.session.query(Professional).filter_by(email=email).first() or \
        db.session.query(Admin).filter_by(email=email).first()
        return user
    app.app_context().push()

    return app

app = create_app()

from application.routes import *
from application.create_initial_data import *

if __name__ =="__main__":
    app.run(debug=True)