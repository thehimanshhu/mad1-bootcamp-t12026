from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key =True , autoincrement=True)
    email = db.Column(db.String, unique=True , nullable=False)
    password = db.Column(db.String , nullable=False)
    

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key =True , autoincrement=True)
    email = db.Column(db.String, unique=True , nullable=False)
    password = db.Column(db.String , nullable=False)
    name = db.Column(db.String , nullable=False)
    address = db.Column(db.String, nullable=False)
    mobile = db.Column(db.String, nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key =True , autoincrement=True)
    name = db.Column(db.String, unique=True , nullable=False)


class Professional(db.Model):
    id = db.Column(db.Integer, primary_key =True , autoincrement=True)
    email = db.Column(db.String, unique=True , nullable=False)
    password = db.Column(db.String , nullable=False)
    name = db.Column(db.String , nullable=False)
    address = db.Column(db.String, nullable=False)
    mobile = db.Column(db.String, nullable=False)
    experiance = db.Column(db.String,nullable = False)
    cat_id = db.Column(db.Integer ,db.ForeginKey("Category.id") , nullable=False )

class Package(db.Model):
    id = db.Column(db.Integer, primary_key =True , autoincrement=True)
    title = db.Column(db.String, unique=True , nullable=False)
    price = db.Column(db.String , nullable=False)
    description= db.Column(db.String , nullable=False)
    cat_id = db.Column(db.Integer ,db.ForeginKey("Category.id") , nullable=False )
    prof_id = db.Column(db.Integer ,db.ForeginKey("Professional.id") , nullable=False )


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key =True , autoincrement=True)
    title = db.Column(db.String, unique=True , nullable=False)
    total_price = db.Column(db.String , nullable=False)
    start_time = db.Column(db.Time , nullable =False)
    end_time = db.Column(db.Time , nullable =False) 
    date = db.Column(db.DateTime , nullable =False)
    cat_id = db.Column(db.Integer ,db.ForeginKey("Category.id") , nullable=False )
    prof_id = db.Column(db.Integer ,db.ForeginKey("Professional.id") , nullable=False )
    pack_id =  db.Column(db.Integer ,db.ForeginKey("Package.id") , nullable=False )
    cust_id = db.Column(db.Integer ,db.ForeginKey("Customer.id") , nullable=False )


