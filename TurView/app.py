from flask import Flask, redirect, render_template, request, send_file
from flask_socketio import SocketIO
import sqlite3
import os
from datetime import datetime
import threading
import queue
import speech_and_text as st
import handle_falcon as hf
import turview_report as tr
import turview_upgraded_cv as cv
import time
import random
import job_descriptions as jd


app = Flask(__name__)
app.config['SECRET_KEY'] = 'enforngtdlbnedjkjtrsxcvbnjktyhyetn'
socketio = SocketIO(app)

# App configuration to accept file uploads
UPLOAD_FOLDER = r"uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

images = {
    1: '/static/Loading.gif',
    2: '/static/TurView_Bot_Greeting.png',
    3: '/static/TurView_Bot_Listening.png',
    4: '/static/TurView_Bot_Speaking1.png',
    5: '/static/TurView_Bot_Speaking2.png'
}

global audio_thread, audio_queue, chatbot_thread, turview_bot, user_id, transcribe, user_dir_path

audio_queue = queue.Queue()
turview_bot = None
audio_thread = None
chatbot_thread = None
transcribe = True

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def history():
    return render_template("history.html", interviews=interviews)


@app.route("/register", methods=['GET', 'POST'])
def register():
    global user_id
    global user_dir_path
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
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
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

        user_dir_path = f"{UPLOAD_FOLDER}\\{user_id}"
        os.mkdir(user_dir_path)

        conn.close()

    elif request.method == "GET":
        return render_template("register.html", designer_job_desc=jd.designer_job_desc, software_job_desc=jd.software_job_desc, consultant_job_desc=jd.consultant_job_desc, stratigist_job_desc=jd.stratigist_job_desc)
    
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
    
    while transcribe:
        while not audio_queue.empty:
            file = audio_queue.get()
            print(f"Transcribing {file}")
            turview_bot.answers_from_user.append = st.transcribe(file)


@app.route("/handle_conversation")
def handle_conversation():
    global turview_bot
    global user_id

    conn = sqlite3.connect("turview.db")
    db = conn.cursor()
    
    db.execute("SELECT name, cv, job_description FROM users WHERE id = ?", (user_id,))
    user_info = db.fetchone()

    user_cv = cv.extract_text(user_info[1])

    initialize_turview_bot(name = user_info[0], cv = user_cv, job_description = user_info[2])
    
    update_info(image_num=2, text="<h4>Welcome to the TurView!</h4>")

    st.say(turview_bot.greetings)
    
    time.sleep(random.uniform(2.5, 5)) # Natural Pause

    for question in range(len(turview_bot.questions)):
        dir_len = check_dir_len(user_dir_path)

        update_info(image_num=5, text=f"<h6>Current Question: {turview_bot.questions[question]}</h6>")
        st.say(turview_bot.questions[question])
        update_info(image_num=2, text=f"<h6>Current Question: {turview_bot.questions[question]}</h6>")

        print("Waiting for User to Answer")
        while True:
            new_dir_len = check_dir_len(user_dir_path)
            if new_dir_len > dir_len:
                break
        print(f"Answer Received for Question #{question + 1}, Proceeding...")
        
        time.sleep(random.uniform(2.5, 5)) # Natural Pause

        if question != 4:
            filler = turview_bot.get_filler()
            update_info(image_num=4, text=f"<h6>{filler}</h6>")
            st.say(filler)
            update_info(image_num=2, text=f"<h6>{filler}</h6>")
            
            time.sleep(random.uniform(2.5, 5)) # Natural Pause
    
    update_info(image_num=4, text="<h4>Thank You for using TurView, your AI-based key to success in interview preperation and career development!</h4>")
    st.say("Thank you for your time and we hope you enjoyed your experience with Ter View!")
    update_info(image_num=2, text="<h4>Your Report is Being Generated!</h4>")

    # Generate Report
    turview_bot.analyze_answers()

    report = tr.TurViewReport()
    questions = report.Questions(turview_bot.questions)
    user_answers = report.Answers(turview_bot.answers_from_user)
    llm_answers = report.Answers(turview_bot.answers_from_llm)

    report = tr.TurViewReport(name=turview_bot.name, job_desc=turview_bot.job_desc_text, questions=questions, user_answers=user_answers, llm_answers=llm_answers, results = turview_bot.results)

    report_path = f"{user_dir_path}/turview_report{user_id}.docx"
    report.write_document(output_path=report_path)

    db.execute("INSERT INTO users (interview report) VALUES (?)", (report_path,))
    conn.commit()

    update_info(image_num=4, text="<h4>Thank You for using TurView, your AI-based key to success in interview preperation and career development!</h4>")
    st.say("You may now view your Ter View Report!")
    update_info(image_num=2, text="<h4>You may now view your TurView Report!</h4>")
    
    # Kill All Threads
    audio_thread.join()
    chatbot_thread.join()
    conn.close()

    return redirect("/report") 


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


@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    global audio_queue
    global user_dir_path

    if 'audio' not in request.files:
        return 'No file part'
    
    audio = request.files['audio']
    audio_id = request.form.get('audioId', None)    

    if audio.filename == '':
        return 'No selected file'
    
    # Save the file to a desired location
    file_path = os.path.join(user_dir_path, f"question_{audio_id}.wav")
    audio.save(file_path)

    audio_queue.put(file_path)

    return 'success' 

@app.route("/report")
def report():
    global user_id
    conn = sqlite3.connect("turview.db")
    db = conn.cursor()

    db.execute("SELECT interview_report FROM users WHERE id = ?", (user_id,))
    report = db.fetchone()[0]

    conn.close()

    return send_file(report)

if __name__ == "__main__":
    socketio.run(app, debug=True)