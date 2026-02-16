from flask import current_app as app
from flask import render_template, request, redirect
from .models import db , Admin , Customer , Professional , Package , Booking

@app.route("/hello")
def index():
    return "hello"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register" , methods=["GET" , "POST"])
def register():
    if request.args.get("role") =='customer' and request.method=="GET":
        return render_template("customer/register.html")
    elif request.args.get("role") =="professional" and request.method=="GET":
        return render_template("professional/register.html")
    elif request.method=="POST" and request.args.get("role") =="customer":
        name = request.form.get("cust_name")
        email = request.form.get("cust_email")
        password = request.form.get("cust_password")
        address = request.form.get("cust_address")
        mobile = request.form.get("cust_mobile")
        cust = db.session.query(Customer).filter_by(email=email).first()
        if cust:
            return "Customer with this email already exists"
        else:
            newcust = Customer(name=name,email=email,password=password,address=address,mobile=mobile)
            db.session.add(newcust)
            db.session.commit()
        return redirect("/customer/dashboard")
    
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/customer/dashboard")
def customer_dashboard():
    return "Welcome to Customer Dashboard"