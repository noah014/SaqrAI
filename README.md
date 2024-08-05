<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TurView - Interview Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        .container {
            width: 80%;
            margin: auto;
            overflow: hidden;
        }
        header {
            background: #333;
            color: #fff;
            padding-top: 30px;
            min-height: 70px;
            border-bottom: #77aadd 3px solid;
        }
        header a {
            color: #fff;
            text-decoration: none;
            text-transform: uppercase;
            font-size: 16px;
        }
        ul {
            padding: 0;
            list-style: none;
        }
        .main {
            margin: 20px 0;
        }
        .main h1 {
            margin-top: 0;
        }
        pre {
            background: #f4f4f4;
            padding: 10px;
            border: 1px solid #ddd;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>TurView - Interview Chatbot for Falcon Hackathon</h1>
        </div>
    </header>
    <div class="container main">
        <h2>Overview</h2>
        <p>Welcome to TurView, an AI-powered interview chatbot developed for the Falcon Hackathon. TurView is designed to revolutionize the interview process by leveraging Falcon's advanced language models and AI71's API Hub. With TurView, users can conduct seamless and intelligent interviews, streamlining the hiring process and enhancing candidate evaluation.</p>

        <h2>Features</h2>
        <ul>
            <li><strong>Automated Interviews:</strong> Conduct interviews using Falcon's powerful language models.</li>
            <li><strong>Audio Transcription:</strong> Convert audio responses to text for easy analysis.</li>
            <li><strong>User Registration:</strong> Securely register users and manage interview data.</li>
            <li><strong>Conversation Handling:</strong> Interactive and dynamic question generation and answer analysis.</li>
            <li><strong>Database Integration:</strong> Store and manage user and interview data using SQLite.</li>
        </ul>

        <h2>Getting Started</h2>
        <h3>Prerequisites</h3>
        <ul>
            <li>Python 3.7+</li>
	    <li>AI71</li>
            <li>Flask</li>
            <li>SQLite3</li>
	    <li>Faster Whisper</li>
	    <li>PyTTSx3</li>
            <li>PyPDF2</li>
            <li>docx2pdf</li>
	    <li>docx2txt</li>
        </ul>

        <h3>Installation</h3>
        <pre>
            <code>
git clone https://github.com/yourusername/turview.git
cd turview
pip install -r requirements.txt
python setup_database.py
flask run
            </code>
        </pre>

        <h3>Configuration</h3>
        <ul>
            <li><strong>Upload Folder:</strong> Configure the upload folder for audio and CV files in the <code>app.config</code> section.</li>
            <li><strong>Secret Key:</strong> Set a secure secret key for session management.</li>
        </ul>

        <h2>Usage</h2>
        <ol>
            <li><strong>Register:</strong> Navigate to the <code>/register</code> route to register a new user and upload their CV and job description.</li>
            <li><strong>Start Interview:</strong> Once registered, go to the <code>/turview</code> route to start the interview process.</li>
            <li><strong>Submit Audio:</strong> Upload audio responses during the interview. The system will transcribe and analyze the responses.</li>
            <li><strong>View History:</strong> Access the <code>/history</code> route to view past interviews and user data.</li>
        </ol>


        <h3>Contributing</h3>
        <ol>
            <li>Fork the repository.</li>
            <li>Create a new branch:
                <pre><code>git checkout -b feature-branch</code></pre>
            </li>
            <li>Make your changes and commit them:
                <pre><code>git commit -m "Add new feature"</code></pre>
            </li>
            <li>Push to the branch:
                <pre><code>git push origin feature-branch</code></pre>
            </li>
            <li>Open a pull request.</li>
        </ol>