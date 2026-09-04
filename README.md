# FaceLogger

#### Video Demo: <URL HERE>

#### Description

FaceLogger is a web application that processes video footage (e.g. CCTV or security camera recordings) to automatically detect human faces, crop them out, and log them with a timestamp, turning long stretches of raw footage into a browsable and timestamped gallery of face captures.

**The problem it addresses:** reviewing security footage after an incident is slow and manual. A person has to scrub through hours of raw video to find the moments a person of interest appeared, and in many cases (e.g. someone wearing a cap or hood to conceal their identity), the footage alone doesn't make identification easy. FaceLogger doesn't solve identity concealment on its own, but it does solve the *scrubbing* problem, now instead of watching an entire video, a user can upload it once and immediately see every moment a face was detected, each with its own cropped image and timestamp ready to be reviewed at a glance.

This was built as a CS50x final project.

## How it works

1. A user uploads a video file through the web interface.
2. The backend samples one frame roughly every second of footage (rather than every single frame, which would be far slower and largely redundant).
3. Each sampled frame is passed through a YOLOv8 model fine-tuned for face detection, which returns a bounding box for every face found.
4. Each detected face is cropped out of the frame and saved as its own image, along with its timestamp (in seconds into the video) and frame number.
5. This metadata is stored in a SQLite database.
6. The dashboard queries this database and displays every captured face as a row in a table: thumbnail, timestamp, and frame number.

## Tech stack

- **Python** / **Flask** — web framework and routing
- **OpenCV** (`opencv-python`) — video reading and frame handling
- **Ultralytics YOLOv8** — face detection model
- **SQLite** (via Python's built-in `sqlite3` module) — storing capture metadata
- **Bootstrap 5** — front-end styling

## File structure

| File | Purpose |
|---|---|
| `app.py` | Flask application: routes for the dashboard and video upload, database initialization |
| `process_video.py` | Core processing pipeline: reads a video, runs face detection, crops and saves faces, writes to the database |
| `templates/layout.html` | Shared page layout (navbar, Bootstrap) |
| `templates/index.html` | Dashboard showing all captured faces |
| `templates/upload.html` | Video upload form |
| `static/captures/` | Saved cropped face images (generated at runtime, not committed to the repo) |
| `uploads/` | Uploaded video files (generated at runtime, not committed to the repo) |
| `facelogger.db` | SQLite database (generated at runtime, not committed to the repo) |
| `requirements.txt` | Python dependencies |
| `yolov8n-face.pt` | Pretrained YOLOv8 nano face-detection weights |

## How to run it locally

1. Clone this repository.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   python app.py
   ```
4. Open `http://127.0.0.1:5000` in your browser.
5. Go to **Upload Video**, choose a video file (`.mp4`, `.mov`, or `.avi`), and submit.
6. You'll be redirected to the dashboard, which shows every face detected in that video along with its timestamp.

No manual database setup is required, the app creates its own SQLite table automatically on first run.

## Design decisions and limitations

**Why sample every ~1 second instead of every frame?** Running face detection on every single frame of a video is computationally wasteful and unnecessary — a person's face doesn't meaningfully change from one frame to the next only 1/30th of a second later. Sampling once per second keeps processing fast while still reliably catching anyone who appears in the footage for more than a moment.

**Why YOLOv8 for detection, and where the weights came from:** the face-detection weights (`yolov8n-face.pt`) are community-trained weights built on the Ultralytics YOLOv8 architecture, trained on the WIDERFace dataset, sourced from [akanametov/yolo-face](https://github.com/akanametov/yolo-face). The nano (`n`) variant was chosen for speed, since the project prioritizes fast, responsive processing over maximum possible detection accuracy.

**No face recognition or deduplication:** an earlier version of this project explored using face *recognition* (via embeddings, e.g. through libraries like `face_recognition`/dlib or InsightFace) to detect when the *same* person reappears across multiple frames, so that a person would only be logged once rather than once per second they're visible. This was scoped out for two reasons: first, `dlib` (a dependency of `face_recognition`) failed to build on Windows without a full Visual Studio C++ toolchain installation, which wasn't a practical use of remaining project time; second, and more fundamentally, the test footage used (wide street-level shots) often placed faces too small/low-resolution in frame for a recognition model to reliably distinguish between individuals. As a result, this version logs *every* detected face at each sampled second, rather than deduplicating repeat appearances of the same person. Extending this project with proper face recognition and deduplication — likely paired with closer-up, higher-resolution footage (e.g. an entrance or checkout camera angle, rather than a wide street view) — is a natural next step.

**Works best with closer-up faces:** because there's no recognition/embedding step, and because the underlying detector performs best on reasonably sized faces, this tool is best suited to footage where faces are a meaningful size in frame (e.g. an entrance camera), rather than very wide, distant shots of a crowd.

**Processing is currently synchronous:** uploading a video causes the server to fully process it before responding. For short clips (tested up to ~30 seconds) this completes in a couple of seconds and isn't noticeable, but a much longer video would leave the browser waiting with no progress feedback. A background-processing approach with live progress updates was considered but scoped out in favor of finishing and polishing the core feature set within the project timeline.

## Credits

**Face detection model:** `yolov8n-face.pt` — pretrained YOLOv8 face-detection weights from [akanametov/yolo-face](https://github.com/akanametov/yolo-face), built on [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) and trained on the WIDERFace dataset.

**Demo footage:** sourced from Pixabay (free to use under the Pixabay license):
- ["Alley People Walk Street Ukraine"](https://pixabay.com/videos/alley-people-walk-street-ukraine-39837/) by [AlexKopeykin](https://pixabay.com/users/alexkopeykin-6178059/)
- ["Ocean Beach Sunset Sea Atmosphere"](https://pixabay.com/videos/ocean-beach-sunset-sea-atmosphere-135658/) by [Natures_Embrace](https://pixabay.com/users/natures_embrace-30639570/)

Video files themselves are not committed to this repository (see `.gitignore`); they are used only for local testing and the demo recording.
