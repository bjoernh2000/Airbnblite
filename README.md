README
=================================
## What is Airbnblite
This small project imitates Airbnb, but just as a lite version. You can signup to be a member to apply for properties, or a renter that rents out their properties. I used Flask sessions to keep track of whether someone is logged in or not. 

## Initialization and packages
Python

Flask - Framework

Mongodb - Database

HTML - Templates

json2html - convert json file into a readable table for html (I didn't really know how to insert a json file into a table on html so I used this package)  - to install "pip install json2html"


## Files and Folders

password.py - functions I created to hash the password of users

database.py - mdsilva/Airbnblite-Tutorial github file to make mongodb easier to use, abstraction of mongodb

app.py - file that includes all the routes

template folder - includes all the templates for the webpages, inc. login, signup, etc.

static folder - a couple bootstrap files
