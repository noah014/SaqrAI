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


@app.route("/register")
def register():
    if request.method == "POST":
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
        

    elif request.method == "GET":
        return render_template("register.html")


if __name__ == "__main__":
    app.run()