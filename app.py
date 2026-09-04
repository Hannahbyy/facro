from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from process_video import process_video
import sqlite3
import os

app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)
allowed_extensions = (".mp4", ".mov", ".avi")

def init_db():
    """Create the captures table if it doesn't already exist (runs on every startup)."""
    conn = sqlite3.connect("facelogger.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            frame INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    """Show every captured face currently stored in the database."""
    conn = sqlite3.connect("facelogger.db")
    rows = conn.execute("SELECT path, timestamp, frame FROM captures").fetchall()
    return render_template("index.html", rows=rows) 

@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Show the upload form (GET), or process an uploaded video (POST)."""
    if request.method == "GET":
        return render_template("upload.html")
    
    elif request.method == "POST":
        if "user_file" not in request.files:
            return "File not received"
        
        file = request.files["user_file"]

        if file.filename == "":
            return "No file was selected"

        elif not file.filename.lower().endswith(allowed_extensions):
            return "Please upload a video file (.mp4, .mov, or .avi)"

        # save the uploaded video, then run the face detection pipeline on it
        filename = secure_filename(file.filename)
        file_path = os.path.join("uploads", filename)
        file.save(file_path)
        process_video(file_path)
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
