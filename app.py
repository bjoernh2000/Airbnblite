from flask import Flask, Response, request, jsonify, render_template, url_for, redirect, flash, session
from flask_pymongo import pymongo
from database import DatabaseConnection
from password import encrypt, is_password
from functools import wraps
from json2html import *

app = Flask(__name__)
db = DatabaseConnection()
app.secret_key = "this is a super secret key"  # session key, I should make this a randomized string

def login_required(f):  # function meaning login is required to access the webpage
    @wraps(f)
    def wrap(*args,**kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first.")
            return redirect(url_for("login"))
    return wrap

def renter_required(f):  # function meaning a renter account is required to access webpage
    @wraps(f)
    def wrap(*args, **kwargs):
        if db.findOne("users",{"username":session["id"]})["user"] == "renter":
            return f(*args,**kwargs)
        else:
            flash("You are not a renter.")
            return redirect("/")
    return wrap

@app.route("/",methods=["GET"])
@login_required
def home():  # general homepage
    return render_template("home.html")

@app.route("/welcome",methods=["GET"])
def welcome():  # site for non-users
    return render_template("welcome.html")

@app.route("/signup",methods=["GET", "POST"])
def signup():  # signup
    error = None
    if request.method == "POST":
        if db.findOne("users", {"username":request.form["username"]}) or db.findOne("users", {"email":request.form["email"]}):
            error = "Email/Username already exists please choose another"
        else:
            document = {
                "email": request.form["email"],
                "username": request.form["username"],
                "password": encrypt(request.form["password"]),
                "user": "customer"
            }
            db.insert("users",document)
            flash("User succesfully added, please login to confirm")
            return redirect(url_for("login"))
    return render_template("signup.html", error=error)

@app.route('/login', methods=["GET", "POST"])
def login():  # login
    error = None
    if request.method == "POST":
        if db.findOne("users", {"email":request.form["email"]}) and db.findOne("users", {"password":encrypt(request.form["password"])}):
            session["logged_in"] = True
            session["id"] = request.form["username"]
            flash("Successfully logged in")
            return redirect(url_for("home"))
        else:
            error = "Invalid Credentials. Please try again."
    if "logged_in" in session:
        flash("You are already logged in")
        return redirect(url_for("home"))
    return render_template("login.html", error=error)

@app.route('/logout', methods=["GET"])
def logout():  # logout
    if "logged_in" in session:
        session.pop("logged_in", None)
        session.pop("id", None)
        flash("Successfully logged out")
    else:
        flash("you are not logged in")
    return redirect(url_for("welcome"))

@app.route("/becomeRenter",methods=["GET"])
@login_required
def becomeRenter():  # become a renter
    if db.findOne("users",{"username":session["id"]})["user"] == "renter":
        flash("you are already a renter!")
        return redirect(url_for("home"))
    db.update("users",{"username":session["id"]}, {'$set':{"user":"renter"}})
    flash("you are now a renter!")
    return redirect(url_for("home"))
    
@app.route("/renterHome",methods=["GET"])
@login_required
@renter_required
def renterHome():  # homepage for renters
    return render_template("renterHome.html")

@app.route("/addNewProperty",methods=["GET","POST"])
@login_required
@renter_required
def addNewProperty():  # add a property
    if request.method == "POST":
        document = {
        "owner": session["id"],
        "name": request.form["name"],
        "price": request.form["price"],
        "address": request.form["address"],
        "rentedBy": "None"
    }
        db.insert("properties", document)
        flash("Property successfully added")
        return redirect(url_for("renterHome"))
    return render_template("addProperties.html")

@app.route("/properties", methods=["GET"])
@login_required
def properties():  # all properties that are not rented
    properties = db.findMany("properties",{"rentedBy":"None"})
    return json2html.convert(json=properties,table_attributes={"style":"width:100%"})

@app.route("/getProperty", methods=["GET","POST"])
@login_required
def getProperty():  # rent a property
    if request.method =="POST":
        if db.findOne("properties",{"name":request.form["name"]}):
            if db.findOne("properties", {"name":request.form["name"]})["rentedBy"] == "None":
                db.update("properties",{"name":request.form["name"]}, {'$set':{"rentedBy":session["id"]}})
                flash("Succefully rented " + request.form["name"])
                return redirect(url_for("home"))
            else:
                flash("This property is already rented")
                return redirect(url_for("home"))
        else:
            flash("No property called " + request.form["name"])
            return redirect(url_for("home"))
    return render_template("getProperty.html")

@app.route("/account", methods=["GET"])
@login_required
def account():  # your account
    return render_template("account.html")

@app.route("/rentedProperties")
@login_required
def rentedProperties():  # your rented properties
    if db.findOne("properties",{"rentedBy":session["id"]}):
        properties = db.findMany("properties",{"rentedBy":session["id"]})
        return json2html.convert(json=properties,table_attributes={"style":"width:100%"})
    else:
        flash("You haven't rented any properties")
        return redirect(url_for("account"))

@app.route("/ownedProperties")
@login_required
@renter_required
def ownedProperties():  # your owned properties
    if db.findOne("properties",{"owner":session["id"]}):
        properties = db.findMany("properties",{"owner":session["id"]})
        return json2html.convert(json=properties,table_attributes={"style":"width:100%"})
    else:
        flash("You don't own any properties")
        return redirect(url_for("account"))


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=4000,debug=True)
