from flask import current_app as app
from flask import render_template, request, redirect , flash
from .models import db , Admin , Customer , Professional , Package , Booking
from flask_login import login_user , login_required ,   current_user , logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  
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
        resume = request.files.get("prof_resume")
        prof = db.session.query(Professional).filter_by(email=email).first()
        if prof:
            return "Professional with this email already exists"
        else:
            resume.save(f"static/{email}.pdf")
            newprof = Professional(name=name,email=email,password=password,address=address,mobile=mobile,experiance=experiance,resume_url=f"static/{email}.pdf",status="Registered")
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

                flash("Invalid password")
                return render_template("login.html" , email=email , password=password)
        else:
            flash("User not found")
            return redirect("/login")

@app.route("/customer/dashboard")
@login_required
def customer_dashboard():
    packs = db.session.query(Package).filter_by(status="Active").all()
    bookings = current_user.bookings
    packages = []
    for pack in packs:
        print(pack.start_date , pack.end_date)
        print(datetime.now().date())
        print(type(pack.start_date) , type(datetime.now().date()))
        if pack.start_date <= datetime.now().date() <= pack.end_date:
            packages.append(pack)
    
    return render_template("customer/dashboard.html" , cu=current_user, packages=packages, bookings=bookings)


@app.route("/professional/dashboard")
@login_required
def professional_dashboard():
    packages = db.session.query(Package).filter_by(prof_id=current_user.id).all()
    print(packages)
    bookings = current_user.bookings
    date = datetime.now().date()
    return render_template("professional/dashboard.html" , cu=current_user, packages=packages, bookings=bookings , today=date)

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():  
    profs = db.session.query(Professional).all()
    customers = db.session.query(Customer).all()
    profs_count = db.session.query(Professional).filter(or_(Professional.status=="Active" , Professional.status=="Flagged" ,Professional.status=="Registered")).count()
    customer_count = db.session.query(Customer).filter(or_(Customer.status=="Active" , Customer.status=="Flagged" ,Customer.status=="Registered")).count()
    return render_template("admin/dashboard.html", cu=current_user, profs=profs , customers=customers, profs_count=profs_count, customer_count=customer_count  )


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
            flash(f"Professional {prof.name} has been flagged. All their packages are now inactive.")
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

@app.route("/customer/book/<int:pack_id>" , methods=["POST"])
@login_required
def book_package(pack_id):
    pack = db.session.query(Package).filter_by(id=pack_id).first()
    date = request.form.get("date")
    time = request.form.get("time")
    
    if pack and pack.status=="Active":
        if pack.start_date <= datetime.strptime(date , "%Y-%m-%d").date() <= pack.end_date:
            newbooking = Booking(cust_id=current_user.id,pack_id=pack_id , prof_id = pack.prof_id , status="Requested" , date =datetime.strptime(date , "%Y-%m-%d").date() , start_time = datetime.strptime(time , "%H:%M").time() , total_price = 0)
            db.session.add(newbooking)
            db.session.commit()
            return redirect("/customer/dashboard")
        else:
            return "Package not available for the selected date"
    else:
        return "Package not available"

@app.route("/professional/<string:action>/<int:booking_id>")
@login_required
def professional_booking_action(action, booking_id):
    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    if booking:
        if action == "accept" and booking.status=="Requested":
            booking.status = "Accepted"
        elif action == "reject" and booking.status=="Requested":
            booking.status = "Rejected"
        db.session.commit()
    return redirect("/professional/dashboard")

@app.route("/admin/professional-details/<int:prof_id>")
@login_required
def professional_details(prof_id):
    prof = db.session.query(Professional).filter_by(id=prof_id).first()
    if prof:
        packages = prof.packages
        bookings = prof.bookings
        return render_template("admin/professional_details.html" ,prof =prof, packages=packages , bookings=bookings)
    else:
        return "Professional not found"


@app.route("/admin/search" , methods=["GET" , "POST"])
def admin_search():
    if request.method=="GET":
        return render_template("admin/search.html")
    elif request.method=="POST":
        query_type=request.form.get("query_type")
        query = request.form.get("query")
        if query_type == "customer":
            customers = db.session.query(Customer).filter(or_(Customer.name.contains(query) , Customer.email.contains(query))).all()
            return render_template("admin/search.html" , results=customers , query_type=query_type , query=query)
        elif query_type == "professional":
            professionals = db.session.query(Professional).filter(or_(Professional.name.contains(query) , Professional.email.contains(query))).all()
            return render_template("admin/search.html" , results=professionals , query_type=query_type , query=query)
        elif query_type == "package":
            packages = db.session.query(Package).filter(or_(Package.title.contains(query) , Package.description.contains(query))).all()
            return render_template("admin/search.html" , results=packages , query_type=query_type , query=query)


@app.route("/admin/statistics")
@login_required
def admin_statistics():
    profs = db.session.query(Professional).all()
    status = ["Active" , "Flagged" , "Registered" , "Rejected"]
    status_count = [0, 0, 0, 0] 
    for prof in profs:
        if prof.status =="Active":
            status_count[0] += 1
        if prof.status =="Flagged":
            status_count[1] += 1
        if prof.status =="Registered":
            status_count[2] += 1
        if prof.status =="Rejected":
            status_count[3] += 1
    plt.bar(status, status_count)
    plt.xlabel("Professional Status")
    plt.ylabel("Count")
    plt.title("Professional Status Distribution")
    plt.savefig("static/prof_status_distribution.png")
    plt.close()

    return render_template("admin/statistics.html", cu=current_user, profs=profs, status=status)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route("/myname" , methods=["POST"])
def myname():
    return "My name is Himanshu"