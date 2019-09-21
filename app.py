from flask import Flask, Response, request, jsonify, render_template, url_for, redirect, flash, session
from flask_pymongo import pymongo
from database import DatabaseConnection
from password import encrypt, is_password
from functools import wraps
from json2html import *
import datetime

app = Flask(__name__)
db = DatabaseConnection()
app.secret_key = "this is a super secret key"

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first.")
            return redirect(url_for("login"))
    return wrap

def renter_required(f):
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
def welcome():
    return render_template("welcome.html")

@app.route("/signup",methods=["GET", "POST"])
def signup():
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
def login():
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
def logout():
    if "logged_in" in session:
        session.pop("logged_in", None)
        session.pop("id", None)
        flash("Successfully logged out")
    else:
        flash("you are not logged in")
    return redirect(url_for("welcome"))

@app.route("/becomeRenter",methods=["GET"])
@login_required
def becomeRenter():
    if db.findOne("users",{"username":session["id"]})["user"] == "renter":
        flash("you are already a renter!")
        return redirect(url_for("home"))
    db.update("users",{"username":session["id"]}, {'$set':{"user":"renter"}})
    flash("you are now a renter!")
    return redirect(url_for("home"))
    
@app.route("/renterHome",methods=["GET"])
@login_required
@renter_required
def renterHome():
    return render_template("renterHome.html")

@app.route("/addNewProperty",methods=["GET","POST"])
def addNewProperty():
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
def properties():
    properties = db.findMany("properties",{"rentedBy":"None"})
    return json2html.convert(json=properties,table_attributes={"style":"width:100%"}) 
    # return render_template("properties.html",data=properties)

@app.route("/getProperty", methods=["GET","POST"])
def getProperty():
    if request.method =="POST":
        if db.findOne("properties",{"name":request.form["name"]})["rentedBy"] == "None":
            db.update("properties",{"name":request.form["name"]}, {'$set':{"rentedBy":session["id"]}})
            flash("Succefully rented this property")
            return redirect(url_for("home"))
        else:
            flash("This property is already rented")
            return redirect(url_for("home"))
    return render_template("getProperty.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=4000,debug=True)
