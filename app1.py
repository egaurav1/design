import cv2
import subprocess
import os
import whisper

VIDEO_PATH = "input/sample1.mp4"

AUDIO_OUTPUT = "output/audio/audio.mp3"

FRAMES_OUTPUT = "output/frames"

TRANSCRIPT_OUTPUT = "output/transcript/transcript.txt"

# ---------------------------------------------------
# CREATE OUTPUT FOLDERS
# ---------------------------------------------------

os.makedirs("output/audio", exist_ok=True)

os.makedirs("output/frames", exist_ok=True)

os.makedirs("output/transcript", exist_ok=True)

# ---------------------------------------------------
# STEP 1: GET VIDEO METADATA
# ---------------------------------------------------

print("\nGetting Video Metadata...\n")

cap = cv2.VideoCapture(VIDEO_PATH)

fps = cap.get(cv2.CAP_PROP_FPS)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

duration = frame_count / fps

print(f"Resolution : {width} x {height}")

print(f"FPS        : {fps}")

print(f"Frames     : {frame_count}")

print(f"Duration   : {duration:.2f} seconds")

# ---------------------------------------------------
# STEP 2: EXTRACT FRAMES
# ---------------------------------------------------

print("\nExtracting Frames...\n")

count = 0
saved = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Save every 30th frame
    if count % 30 == 0:

        filename = os.path.join(
            FRAMES_OUTPUT,
            f"frame_{saved}.jpg"
        )

        cv2.imwrite(filename, frame)

        saved += 1

    count += 1

cap.release()

print(f"Saved {saved} frames")

# ---------------------------------------------------
# STEP 3: EXTRACT AUDIO
# ---------------------------------------------------

print("\nExtracting Audio...\n")

command = [
    "ffmpeg",
    "-i", VIDEO_PATH,
    "-q:a", "0",
    "-map", "a",
    "-y",
    AUDIO_OUTPUT
]

subprocess.run(command)

print("Audio extracted successfully!")

# ---------------------------------------------------
# STEP 4: AUDIO TO TEXT
# ---------------------------------------------------

print("\nConverting Audio to Text...\n")

model = whisper.load_model("base")

result = model.transcribe(AUDIO_OUTPUT)

transcript = result["text"]

# Save transcript
with open(TRANSCRIPT_OUTPUT, "w", encoding="utf-8") as f:

    f.write(transcript)

print("\nTranscript:\n")

print(transcript)

print("\nTranscript saved successfully!")

print("\nProject Completed!")