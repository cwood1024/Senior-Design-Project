import cv2
import os

def frame_break(video_path, output_directory):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    frame_count = 0
    
    # Loop through the frames
    while True:
        ret, frame = cap.read()  # Read the next frame
        if not ret:
            break  # End of video

        frame_filename = os.path.join(output_directory, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_filename, frame)

        frame_count += 1

    # Release the VideoCapture
    cap.release()
