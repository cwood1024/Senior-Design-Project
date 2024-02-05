import mediapipe as mp
import cv2
import os
import sqlite3
from pose_detect import detect_pose
from frame_break import frame_break
from prettytable import PrettyTable

def clear_frames(output_dir):
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def get_next_video_name(output_directory, base_name):
    existing_videos = [f for f in os.listdir(output_directory) if f.endswith(".mp4")]
    index = 1
    while True:
        video_name = f"{base_name}{index}.mp4"
        if video_name in existing_videos:
            index += 1
        else:
            return video_name
        
def print_database_output(cursor):
    # Fetch all data from the database
    cursor.execute('SELECT * FROM hitters')
    hitters_data = cursor.fetchall()

    # Create a PrettyTable instance and add columns
    table = PrettyTable()
    table.field_names = ["Hitter Name", "Hitting Side", "Stance Width", "Video Location"]

    # Add data to the table
    for row in hitters_data:
        table.add_row(row[1:])  # Exclude the 'id' column
        
    print(table)

def hitter_analysis():
    # Set the input video file path
    initial_input_video_path = input("Enter the input video file path (without quotation marks): ")
    
    # Database code       
    conn = sqlite3.connect('hitters_data.db')
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS hitters (
            id INTEGER PRIMARY KEY,
            hitter_name TEXT,
            hitting_side TEXT, 
            stance_width TEXT,
            video_location TEXT     
            )'''
        )
    conn.commit()

    # Set the MLB hitters database file path
    mlb_database_path = "C:\SeniorDesign\mlb_hitters_data.db"
    second_conn = sqlite3.connect(mlb_database_path)
    second_cursor = second_conn.cursor()
    mlb_output_path = ""
    output_video_path = ""

    # Clip input video into individual frames
    output_directory = "output_frames"
    clear_frames(output_directory)
    frame_break(initial_input_video_path, output_directory)
    print("The video has been broken down into frames")
    cap = cv2.VideoCapture(initial_input_video_path)
    output_video_path = None

    frame_counter = 0
    max_frame_count = 5

    # Initialize mediapipe modules for pose and object detection
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    # Create a VideoWriter object
    output_video_base_name = "output_video"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Specify the video codec
    out = None

    while True: 
        hitter_name = input("Enter the hitter's name: ")

        while True:
            ret, frame = cap.read()  # Read the next frame
            if not ret:
                break  # End of video

            frame_filename = os.path.join(output_directory, f"frame_{frame_counter:04d}.jpg")
            cv2.imwrite(frame_filename, frame)

            frame_counter += 1

            # Print the frame number being processed
            print("Processing frame:", f"frame_{frame_counter:04d}.jpg")

            # Perform pose and object detection
            results_pose = detect_pose(frame)

            if results_pose.pose_landmarks and frame_counter < max_frame_count:
                # Your classification logic here
                knee_distance = abs(results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].x - results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].x)
                shoulder_distance = abs(results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x - results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x)

                if abs(results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x > results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x):
                    hitting_side = "Right Handed Hitter"
                else:
                    hitting_side = "Left Handed Hitter"

                if hitting_side == "Right Handed Hitter":
                    if knee_distance > shoulder_distance:
                        stance_width = "Wide"
                        print("Right-handed wide stance hitter.")
                    else:
                        stance_width = "Narrow"
                        print("Right-handed narrow stance hitter.")
                else:
                    if knee_distance > shoulder_distance:
                        stance_width = "Wide"
                        print("Left-handed wide stance hitter.")
                    else:
                        stance_width = "Narrow"
                        print("Left-handed narrow stance hitter.")

            # Draw landmarks on the frame
            mp_drawing.draw_landmarks(frame, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Write the frame to the output video
            if out is None:
                height, width, _ = frame.shape
                output_video_name = get_next_video_name("output_vids", output_video_base_name)
                output_video_path = os.path.join("output_vids", output_video_name)
                out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (width, height))
            out.write(frame)

            # Insert data into the database
            cursor.execute('''
                INSERT INTO hitters (hitter_name, hitting_side, stance_width, video_location)
                VALUES (?, ?, ?, ?)
            ''', (hitter_name, hitting_side, stance_width, output_video_path))
            conn.commit()

        print("File location of video:", output_video_path)
       

        # Compare user's data with the data in the second database
        second_cursor.execute('SELECT * FROM hitters WHERE hitting_side = ? AND stance_width = ?', (hitting_side, stance_width))
        mlb_output = second_cursor.fetchone()

        if mlb_output:
            # Perform the comparison logic here based on your requirements
            print("User's data:", (hitting_side, stance_width))
            print("Data from the second database:", mlb_output)

        # Print database output
        second_cursor.execute('SELECT * FROM hitters WHERE video_location = ?', (mlb_database_path,))
        mlb_output = second_cursor.fetchone()
        
        mlb_output_path = mlb_output[-1]  # Get the file location from the last element
        print("MLB Output Path:", mlb_output_path)
        
            #print("No MLB output found in the database.")
            #mlb_output_path = "C:\SeniorDesign\mlb_hitters_processed"  # Set a default path

        # Release the VideoWriter
        if out is not None:
            out.release()

        # Release the VideoCapture
        cap.release()

        # Clear the individual frames
        clear_frames(output_directory)

        conn.close()
        second_conn.close()

        return output_video_path, mlb_output