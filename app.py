from flask import Flask, Response, request, jsonify, render_template
from flask_pymongo import pymongo
from database import DatabaseConnection
import datetime

app = Flask(__name__)
db = DatabaseConnection()

@app.route("/addNewProperty",methods=["POST"])
def addNewProperty():
    document = {
        "name": request.form["name"],
        "propertyType": request.form["type"],
        "price": request.form["price"]
    }
    db.insert("properties", document)
    return Response("Property successfully added", status=200, content_type="text/html")

@app.route("/properties", methods=["GET"])
def getProperties():
    properties = db.findMany("properties", {})
    return jsonify(properties)

@app.route("/",methods=["GET"])
def hello():
    return Response("<h1> Hello there </h1>",status=200,content_type="text/html")

@app.route("/welcome",methods=["GET"])
def welcome():
    return render_template("welcome.html")

@app.route("/greeting",methods=["POST"])
def greeting():
    name = request.form["name"]
    hourOfDay = datetime.datetime.now().time().hour
    if not name:
        return Response(status=404)
    if hourOfDay < 12:
        greeting = "Good Morning"
    elif hourOfDay > 12 and hourOfDay < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    response = greeting + " " + name + "!"
    return Response(response, status=200,content_type="text/html")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=4000,debug=True)
