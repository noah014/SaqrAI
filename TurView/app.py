from flask import Flask, flash, redirect, render_template, request
import sqlite3
import os


'''
database schema

table 1: id, interview date and time, interviwee name 
table 2: interview id, user_id, intervieww cv (link), job description, interview report(link)
'''

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def history():
    conn = sqlite3.connect("TurView/turview.db")
    db = conn.cursor()

    return render_template("history.html", interviews=interviews)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        ...

        
    elif request.method == "GET":
        return render_template("register.html")
    
    return redirect("/turview")

    
@app.route("/turview")
def turview():
    return render_template("turview.html")


if __name__ == "__main__":
    app.run()