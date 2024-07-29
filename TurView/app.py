from flask import Flask, flash, redirect, render_template, request
import sqlite3


'''
database schema

table 1: id, interview date and time, interviwee name #temp
table 2: id, intervieww cv (link), job description, interview report(link)
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

