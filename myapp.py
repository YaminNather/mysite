from flask import Flask, render_template, request, Response, redirect, url_for
import sqlite3
import os

currentdirectory = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/", methods = ["POST"])
def phonebook():
    name = request.form["Name"]
    phoneno = request.form["PhNo"]
    connection = sqlite3.connect(currentdirectory + "\Faculty.db")
    cursor = connection.cursor()
    query1 = "INSERT INTO facultylist VALUES ('{n}',{pnm})".format(n = name, pnm = phoneno)
    cursor.execute(query1)
    connection.commit()

    return redirect(url_for('resultpage'))

@app.route("/resultpage", methods=["GET"])
def resultpage():
    try:
        if request.method == "GET":
            name = request.args.get("Name")
            connection = sqlite3.connect(currentdirectory + "\Faculty.db")
            cursor = connection.cursor()
            query1 = "SELECT PhNo from facultylist WHERE Name = {n}".format(n = name)
            result = cursor.execute(query1)
            result = result.fetchall()[0]
            #result = result.fetchall()
            connection.commit()

            return render_template("resultpage.html", Phonenumber = result)
        
    except:
        return render_template("resultpage.html", Phonenumber = "")
    
@app.route("/display")
def display():
    connection = sqlite3.connect(currentdirectory + "\Faculty.db")
    cursor = connection.cursor()
    query1 = "SELECT * from 'facultylist'"
    result = cursor.execute(query1)
    result = result.fetchall()
    connection.commit()

    return render_template("display.html", usr = result)


if __name__ == "__main__":
    app.run()