from flask import Flask, flash, redirect, render_template, request, session
import sqlite3
import os
from datetime import datetime
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

import speech_and_text as st
import handle_falcon as hf
# import turview_report as tr
import turview_upgraded_cv as cv
import util

import time
import random

'''
database schema

table users: id, interview date and time, interviwee name 
table interviews: interview id, user_id, interview cv (link), job description, interview report(link)
'''

app = Flask(__name__)

# App configuration to accept file uploads
UPLOAD_FOLDER = r"..\TurView\uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Session key
app.secret_key = 'f379f632024d5d4b6f09e4f2e30c3cd87ec392e67f07958be0b5c4284b803051'

global audio_thread, audio_queue, chatbot_thread, turview_bot, user_id

audio_queue = queue.Queue()
turview_bot = None
audio_thread = None
chatbot_thread = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def history():
    return render_template("history.html", interviews=interviews)


@app.route("/register", methods=['GET', 'POST'])
def register():
    conn = sqlite3.connect("turview.db")
    db = conn.cursor()
    global user_id
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
        if request.form.get("job_desc"):
            job_desc = request.form.get("job_desc")
        
        elif request.form.get("job_desc") == 5 and request.form.get("job_desc_input"):
            job_desc = request.form.get("job_desc_input")
            
        else:
            return 'Please enter your job description' 

        # Save info to the database 
        db.execute("INSERT INTO users (datetime, name, cv, job_description) VALUES (?, ?, ?, ?)", (datetime.today().strftime('%Y-%m-%d %H:%M:%S'), name, filepath, job_desc))
        conn.commit()
        
        # log the user
        db.execute("SELECT id FROM users WHERE name = ? AND cv = ? and job_description = ?", (name, filepath, job_desc))
        user_id = int(db.fetchone()[0])

        db.close()

    elif request.method == "GET":
        return render_template("register.html")
    
    return redirect("/turview")


@app.route("/turview", methods=['GET', 'POST'])
def turview():
    global chatbot_thread
    global audio_thread

    if request.method == "POST":
        if 'audio_data' not in request.files:
            return 'No file part'
    
        file = request.files['audio_data']
        
        if file.filename == '':
            return 'No selected file'
        
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'audio.webm')
        file.save(filepath)

        process_audio(filepath)

    elif request.method == "GET":
        chatbot_thread = threading.Thread(target = handle_conversation)
        chatbot_thread.daemon = False
        chatbot_thread.start()
        
        audio_thread = threading.Thread(target = handle_transcription)
        audio_thread.daemon = False
        audio_thread.start()
        
        return render_template("turview.html")


def initialize_turview_bot(name, cv, job_description):
    global turview_bot
    st.say("Welcome to Ter View! Your Ter Viewer will be with you shortly!")
    turview_bot = hf.FalconChatbot(name = name, cv_text = cv, job_desc_text = job_description)


def handle_transcription():
    print("Transcription Started")
    
    while not audio_queue.empty:
        turview_bot.answers_from_user.append = st.transcribe(audio_queue.get())


@app.route("/handle_conversation")
def handle_conversation():
    global turview_bot
    global user_id

    conn = sqlite3.connect("turview.db")
    db = conn.cursor()
    
    db.execute("SELECT name, cv, job_description FROM users WHERE id = ?", (user_id,))
    user_info = db.fetchone()

    user_cv = cv.extract_text(user_info[1])

    update_state(image_num=4, text="Your TurViewer is Preparing to Interview You, Please Wait!")
    initialize_turview_bot(name = user_info[0], cv = user_cv, job_description = user_info[2])
    
    update_state(image_num=3, text="Welcome to the TurView!")
    st.say(turview_bot.greetings)
    update_state(image_num=0, text="Welcome to the TurView!")
    time.sleep(random.uniform(2.5, 5)) # Natural Pause

    for question in range(len(turview_bot.questions)):
        update_state(image_num=2, text=turview_bot.questions[question])
        time.sleep(random.uniform(2.5, 5)) # Natural Pause
        st.say(turview_bot.questions[question])
        update_state(image_num=1, text=turview_bot.questions[question])

        # when record pressed
        # listening face
        update_state(image_num=1, text=turview_bot.questions[question])
        if 'file' not in request.files:
            return 'No file part'
        
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No selected file'}
        
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, f'recording_{question}.wav')
            file.save(filepath)
            audio_queue.put()  # Pass the file path to the transcription thread

        # time.sleep(random(2.5, 5)) # Natural Pause

        filler = turview_bot.get_filler()
        update_state(image_num=3, text=filler)
        st.say(filler)
        update_state(image_num=1, text=f"Next Question, Question {question + 1}")
        time.sleep(random.uniform(2.5, 5)) # Natural Pause
    
    st.say("Thank you for your time and we hope you enjoyed your experience with Ter View! Now you may view your Ter View Report!")

    # provide report

    # Kill All Threads
    audio_thread.join()
    chatbot_thread.join()


@app.route("/update_state", methods=["POST"])
def update_state(image_num: int, text: str):
    return {"image_num": image_num, "text": text}
    

def process_audio(filepath):
    ...
    
if __name__ == "__main__":
    app.run()


'''    conn = sqlite3.connect("turview.db")
    db = conn.cursor()


    def handle_transcription(turview_bot, question, filepath):
        turview_bot.answers_from_user[question] = st.transcribe(filepath)

    def handle_conversation(turview_bot, audio_queue):
        for question in range(len(turview_bot.questions)):
            # say question
            # speakinmg face
            st.say(turview_bot.questions[question])
            # greeting face
            # when record pressed
            # listening face
            if 'file' not in request.files:
                return 'No file part'
            
            file = request.files['file']
            if file.filename == '':
                return {'error': 'No selected file'}
            
            if file:
                filepath = os.path.join(UPLOAD_FOLDER, f'recording_{question}.wav')
                file.save(filepath)
                audio_queue.put()  # Pass the file path to the transcription thread
            # when recording done --> greeting face
            
            # set speaking2 image --> JS
            # capture audio and post to processing thread
            # wait for audio to come in.
            # put audio in queue

            st.say(turview_bot.get_filler())
            
    if request.method == "POST":
        # Query the Database for the user's information
        user_info = db.execute("SELECT name, cv, job_description FROM users WHERE id = ?", session["user_id"])
        user_cv = cv.extract_text(user_info[1])

        # Initialize the chatbot
        turview_bot = hf.FalconChatbot(name = user_info[0], cv = user_cv, job_description = user_info[2])
        st.say(turview_bot.greetings)
        
        # here

       # Start thread for conversation
        conversation_thread = threading.Thread(target=handle_conversation, args=(turview_bot, audio_queue))
        
        # Start ThreadPoolExecutor for transcription
        with ThreadPoolExecutor(max_workers=5) as executor:
            conversation_thread.start()
            
            while conversation_thread.is_alive() or not audio_queue.empty():
                try:
                    question, filepath = audio_queue.get(timeout=90)
                    executor.submit(handle_transcription, turview_bot, question, filepath)
                except queue.Empty:
                    continue
            
            conversation_thread.join()

        # say goodbye
        st.say("""Thank you for your time and we hope you enjoyed your experience with Ter View! 
            Now you may view your Ter View Report!""")
        # present user with report '''