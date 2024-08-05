import base64
from flask import Flask, flash, json, jsonify, redirect, render_template, request
from flask_socketio import SocketIO, emit
import sqlite3
import os
from datetime import datetime
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

import speech_and_text as st
import handle_falcon as hf
import turview_report as tr
import turview_upgraded_cv as cv
import time
import random




app = Flask(__name__)
app.config['SECRET_KEY'] = 'enforngtdlbnedjkjtrsxcvbnjktyhyetn'
socketio = SocketIO(app)


# App configuration to accept file uploads
UPLOAD_FOLDER = r"C:\Users\ahmad\OneDrive\Documents\SaqrAI\TurView\uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

images = {
    1: '/static/Loading.gif',
    2: '/static/TurView_Bot_Greeting.png',
    3: '/static/TurView_Bot_Listening.png',
    4: '/static/TurView_Bot_Speaking1.png',
    5: '/static/TurView_Bot_Speaking2.png'
}

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
    global user_id
    if request.method == "POST":
        # Connect to the database
        conn = sqlite3.connect("turview.db")
        db = conn.cursor()

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


        conn.close()

    elif request.method == "GET":
        return render_template("register.html")
    
    return redirect("/turview")


@app.route("/turview")
def turview():
    global chatbot_thread
    global audio_thread
    global audio_queue

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

    # util.update_state(image_num=4, text="Your TurViewer is Preparing to Interview You, Please Wait!")
    initialize_turview_bot(name = user_info[0], cv = user_cv, job_description = user_info[2])
    
    update_info(image_num=2, text="<h4>Welcome to the TurView!</h4>")

    st.say(turview_bot.greetings)
    # util.update_state(image_num=0, text="Welcome to the TurView!")
    time.sleep(random.uniform(2.5, 5)) # Natural Pause

    for question in range(len(turview_bot.questions)):
        dir_len = check_dir_len(r"TurView\uploads")

        update_info(image_num=5, text=f"<h6>Current Question: </h6>{turview_bot.questions[question]}")
        st.say(turview_bot.questions[question])

        ### js ###
        # when record pressed
        # listening face
        # util.update_state(image_num=1, text=turview_bot.questions[question])
        ### js ####
        
        while True:
            new_dir_len = check_dir_len(r"TurView\uploads")
            if new_dir_len > dir_len:
                break

        time.sleep(random(2.5, 5)) # Natural Pause

        filler = turview_bot.get_filler()
        # util.update_state(image_num=3, text=filler)
        st.say(filler)
        # util.update_state(image_num=1, text=f"Next Question, Question {question + 1}")
        time.sleep(random.uniform(2.5, 5)) # Natural Pause
    
    st.say("Thank you for your time and we hope you enjoyed your experience with Ter View! Now you may view your Ter View Report!")

    # provide report

    # Kill All Threads
    audio_thread.join()
    chatbot_thread.join()


def check_dir_len(dir_path):
    dir_len = 0
    if os.path.isdir(dir_path):
        for file in os.listdir(dir_path):
            if file.endswith(".wav"):
                dir_len += 1
    return dir_len


def update_info(image_num: int, text: str):
    img_src = images.get(image_num, '')
    socketio.emit('update_info', {
        'newMessage': text,
        'newImageURL': img_src
    })

    print(f"Current message updated to: {text}")
    print(f"Current image updated to: {img_src}")


@socketio.on('message')
def handle_audio(data):
    global user_id

    # Decode the incoming data
    message = json.loads(data)
    audio_data = message['audioData']
    audio_id = message['audioId']

    # Decode the base64 string to binary data
    audio_bytes = base64.b64decode(audio_data)

    # Save the audio data with a unique file name
    file_path = os.path.join(UPLOAD_FOLDER, f'{audio_id}.wav')
    with open(file_path, 'wb') as f:
        f.write(audio_bytes)
    
    print(f"Audio saved to {file_path}")
    emit('response', {'message': f'Audio {audio_id} received and saved!'})



if __name__ == "__main__":
    socketio.run(app, debug=True)
