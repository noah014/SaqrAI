from flask import Flask, flash, redirect, render_template, request, session
import sqlite3
import os
from datetime import datetime

import speech_and_text as st
import handle_falcon as hf
# import turview_report as tr
import turview_upgraded_cv as cv
import util

'''
database schema

table users: id, interview date and time, interviwee name 
table interviews: interview id, user_id, interview cv (link), job description, interview report(link)
'''

conn = sqlite3.connect("turview.db")
db = conn.cursor()

app = Flask(__name__)

# App configuration to accept file uploads
UPLOAD_FOLDER = r"TurView\uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Session key
app.secret_key = 'f379f632024d5d4b6f09e4f2e30c3cd87ec392e67f07958be0b5c4284b803051'


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def history():
    return render_template("history.html", interviews=interviews)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        # Get the name
        name = request.form.get("name")

        # Get the cv
        if 'file' not in request.files:
            return 'No file part', 400

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty part
        if file.filename == '':
            return 'No selected file', 400

        # Save the file to the specified upload folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Get the job description
        job_desc = request.form.get("job_desc")
        if job_desc == 5 and request.form.get("job_desc_input"):
            job_desc = request.form.get("job_desc_input")
        else:
            return 'Please enter your job description' 

        # Save info to the database 
        db.execute("INSERT INTO users (datetime, name, cv, job_description) VALUES (?, ?, ?, ?)", (datetime.today(), name, filepath, job_desc))
        db.commit()
        
        # log the user
        id = db.execute("SELECT id FROM users WHERE name = ? AND cv = ? and job_description = ?", (name, filepath, job_desc))
        session["id"] = id

    elif request.method == "GET":
        return render_template("register.html")
    
    return redirect("/turview")

@app.route("/turview", methods=['GET', 'POST'])
def turview():

    if request.method == "POST":
        # Query the Database for the user's information
        user_info = db.execute("SELECT name, cv, job_description FROM users WHERE id = ?", session["id"])
        user_cv = cv.extract_text(user_info[1])
        
        # set loading gif image

        # Initialize the chatbot
        turview_bot = hf.FalconChatbot(name = user_info[0], cv = user_cv, job_description = user_info[2])

        # set greeting image
        st.say(turview_bot.greetings)
        
        # START LOOP
        for question in range(5): # 0=Q1, 1=Q2, 2=Q3, 3=Q4, 4=Q5
            # set speaking1 image --> JS

            # say question
            st.say(turview_bot.questions[question])
            # set greeting/standby image --> JS

            # user presses record --> JS
            # set listening image --> JS
            # python WAITS for js audio to come in
            
            if 'file' not in request.files:
                return 'No file part'
            
            file = request.files['file']
            if file.filename == '':
                return {'error': 'No selected file'}
            
            if file:
                filepath = os.path.join(UPLOAD_FOLDER, 'recording.wav')
                file.save(filepath)
                turview_bot.answers_from_user[question] = st.transcribe(filepath)

            # set speaking2 image --> JS
            # capture audio and post to processing thread
            st.say(turview_bot.get_filler())
        # END LOOP
        

        # To use in a Thread for generating questions

            # join threads

        # for each question:
        # Thread to handle the conversation: questioning, listening --> q2 **for ex**

        # Thread to handle conversation analysis: genereate ideal answers, compapre the user answer to the ideal answer  --> q1 **for ex**

        # join threads
        # 5 questions
        for INDEX in range(5):
            ...

    elif request.method == "GET":
        return render_template("turview.html")

if __name__ == "__main__":
    app.run()