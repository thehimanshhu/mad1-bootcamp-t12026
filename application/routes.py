from flask import current_app as app
from flask import render_template, request, redirect
from .models import db , Admin , Customer , Professional , Package , Booking
from flask_login import login_user , login_required ,   current_user
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
        return redirect("/login")
    elif request.method=="POST" and request.args.get("role") =="professional":
        name = request.form.get("prof_name")
        email = request.form.get("prof_email")
        password = request.form.get("prof_password")
        address = request.form.get("prof_address")
        mobile = request.form.get("prof_mobile")
        experiance = request.form.get("prof_experiance")
        prof = db.session.query(Professional).filter_by(email=email).first()
        if prof:
            return "Professional with this email already exists"
        else:
            newprof = Professional(name=name,email=email,password=password,address=address,mobile=mobile,experiance=experiance,resume_url="dummy",status="pending")
            db.session.add(newprof)
            db.session.commit()
        return redirect("/login")
    
@app.route("/login" , methods=["GET" , "POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    elif request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.session.query(Customer).filter_by(email=email).first() or \
                db.session.query(Professional).filter_by(email=email).first() or \
                db.session.query(Admin).filter_by(email=email).first()
        if user :
            if user.password == password:
                if isinstance(user , Admin):
                    login_user(user)
                    return redirect("/admin/dashboard")
                elif isinstance(user , Professional):
                    login_user(user)
                    return redirect("/professional/dashboard")  
                elif isinstance(user , Customer):
                    login_user(user)
                    return redirect("/customer/dashboard")
            else:
                return "Invalid password"
        else:
            return "User not found"

@app.route("/customer/dashboard")
@login_required
def customer_dashboard():
    return f"Welcome to Customer Dashboard {current_user.name} and email is {current_user.email }"


@app.route("/professional/dashboard")
@login_required
def professional_dashboard():
    return f"Welcome to Professional Dashboard {current_user.name} and email is {current_user.email}"

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():  
    profs = db.session.query(Professional).all()
    customers = db.session.query(Customer).all()
    return render_template("admin/dashboard.html", cu=current_user, profs=profs , customers=customers)