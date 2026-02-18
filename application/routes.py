from flask import current_app as app
from flask import render_template, request, redirect
from .models import db , Admin , Customer , Professional , Package , Booking
from flask_login import login_user , login_required ,   current_user , logout_user
from datetime import datetime
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
    packs = db.session.query(Package).filter_by(status="Active").all()
    return render_template("customer/dashboard.html" , cu=current_user, packages=packs)


@app.route("/professional/dashboard")
@login_required
def professional_dashboard():
    packages = db.session.query(Package).filter_by(prof_id=current_user.id).all()
    return render_template("professional/dashboard.html" , cu=current_user, packages=packages)

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():  
    profs = db.session.query(Professional).all()
    customers = db.session.query(Customer).all()
    return render_template("admin/dashboard.html", cu=current_user, profs=profs , customers=customers)


@app.route("/admin/professional/<string:action>/<int:prof_id>")
@login_required
def approve_professional(action, prof_id):
    prof = db.session.query(Professional).filter_by(id=prof_id).first()
    if prof:
        if action =="Accept"  and prof.status=="Registered":
            prof.status = "Active"
            db.session.commit()
        elif action =="Reject" and prof.status=="Registered":
            prof.status = "Rejected"
            db.session.commit()
        elif action =="Flag" and prof.status=="Active":
            prof.status = "Flagged"
            for package in prof.packages:
                package.status = "Inactive"
            db.session.commit()
        elif action =="Unflag" and prof.status=="Flagged":
            prof.status = "Active"
            for package in prof.packages:
                package.status = "Active"
            db.session.commit()
        else:
            return "Invalid action or status"
    else:
        return "Professional not found"
    return redirect("/admin/dashboard")


@app.route("/admin/customer/<string:action>/<int:cust_id>")
@login_required
def flag_customer(action, cust_id):
    cust = db.session.query(Customer).filter_by(id=cust_id).first()
    if cust:
        if action =="Flag" and cust.status=="Active":
            cust.status = "Flagged"
            db.session.commit()
        elif action =="Unflag" and cust.status=="Flagged":
            cust.status = "Active"
            db.session.commit()
        else:
            return "Invalid action or status"
    else:
        return "Customer not found"
    return redirect("/admin/dashboard")


@app.route("/professional/add_package" , methods=["POST"])
@login_required
def add_package():
    title = request.form.get("title")
    description = request.form.get("description")
    price = request.form.get("price")
    start_date = datetime.strptime( request.form.get("start_date") , "%Y-%m-%d").date()
    end_date = datetime.strptime( request.form.get("end_date") , "%Y-%m-%d").date()
    pack = db.session.query(Package).filter_by(title=title).first()
    if pack:
        return "Package with this title already exists"
    else:
        newpack = Package(title=title,description=description,price=price,start_date=start_date,end_date=end_date,prof_id=current_user.id,status="Active")
        db.session.add(newpack)
        db.session.commit()
    return redirect("/professional/dashboard")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")