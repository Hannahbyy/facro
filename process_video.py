import cv2
from ultralytics import YOLO
import os
import sqlite3

def process_video(video_path):
    """Detect faces in a video, crop them, and log each capture to the database."""

    model = YOLO("yolov8n-face.pt") # load the face-detection model
    os.makedirs("static/captures", exist_ok=True) # make sure the output folder exists
    cap = cv2.VideoCapture(video_path)

    # clear out any captures from a previous run before processing this video
    conn = sqlite3.connect("facelogger.db")
    conn.execute("DELETE FROM captures")
    conn.commit()

    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"FPS: {fps}")

    frame_number = 0
    frame_interval = int(fps)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("End of Video")
            break

        # only run detection once per second of footage, not on every frame
        if frame_number % frame_interval == 0:
            results = model(frame)
            result = results[0]
            num_faces = len(result.boxes)

            for i, box in enumerate(result.boxes):
                # get the bounding box coordinates and crop out just the face
                xyxy = box.xyxy[0]
                x1, y1, x2, y2 = map(int, xyxy)
                face_crop = frame[y1:y2, x1:x2]

                timestamp = round(frame_number / fps, 3)
                file_path = f"captures/frame{frame_number}_face{i}.jpg"  # path stored in the DB (relative to static/)
                save_path = f"static/captures/frame{frame_number}_face{i}.jpg"  # actual path on disk
                cv2.imwrite(save_path, face_crop)

                conn.execute("INSERT INTO captures (path, timestamp, frame) VALUES (?, ?, ?)", (file_path, str(timestamp), frame_number))

            print(f"Frame {frame_number}: {num_faces} face(s) detected")

        frame_number += 1

    conn.commit()
    conn.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # allows this script to be run standalone for testing
    process_video("sample.mp4") 