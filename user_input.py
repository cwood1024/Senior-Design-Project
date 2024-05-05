import mediapipe as mp
import cv2
import os
import sqlite3
from pose_detect import detect_pose
from frame_break import frame_break
from prettytable import PrettyTable
import xml.etree.ElementTree as ET
import numpy as np
import torch



def load_yolov5_model():
    return torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

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
    table.field_names = ["Hitter Name", "Hitting Side", "Stance Width", "Weight Distribution", "Spilling Over", "Video Location"]

    # Add data to the table
    for row in hitters_data:
        table.add_row(row[1:])  # Exclude the 'id' column
        
    print(table)

def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def hitter_analysis():

    output_video_path = None
    mlb_output_path = None

    print("Output video path:", output_video_path)
    print("MLB output path:", mlb_output_path)

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
            weight_distribution TEXT,
            spilling_over TEXT,
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
    model = load_yolov5_model()
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

            # Perform object detection using YOLOv5
            results_yolo = model(frame)

            # Render the detected objects on the frame
            detected_frame = results_yolo.render()[0]

            # Resize the frame for display
            display_frame = cv2.resize(detected_frame, (1920, 1080))

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
                    else:
                        stance_width = "Narrow"
                else:
                    if knee_distance > shoulder_distance:
                        stance_width = "Wide"
                    else:
                        stance_width = "Narrow"
                
                
            landmarks = results_pose.pose_landmarks.landmark
            hip = (landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y)
            knee = (landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x ,
                    landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y )
            ankle = (landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x ,
                    landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y )
            
            if landmarks is not None:
                # Analyze alignment - stack the back side
                back_line = np.array([hip, knee, ankle])
                alignment_error = np.linalg.norm(np.cross(back_line[1] - back_line[0], back_line[0] - back_line[2])) / np.linalg.norm(back_line[1] - back_line[0])

                # Check for hip hinge
                hip_hinge = calculate_angle(hip, knee, ankle)

                # Check weight distribution
                weight_distribution = 'balanced' if hip_hinge < 85 else 'over'

                # Assess spilling over
                spilling_over = 'yes' if hip_hinge > 90 else 'no'

                # Draw landmarks on the frame
                mp_drawing.draw_landmarks(frame, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            else:
                print("Pose landmarks not found.")

            # Write the frame to the output video
            if out is None:
                height, width, _ = frame.shape
                output_video_name = get_next_video_name("output_vids", output_video_base_name)
                output_video_path = os.path.join("output_vids", output_video_name)
                out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (width, height))
            out.write(frame)
            out.write(detected_frame)


            # Insert data into the database
            cursor.execute('''
                INSERT INTO hitters (hitter_name, hitting_side, stance_width, weight_distribution, spilling_over, video_location)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (hitter_name, hitting_side, stance_width, weight_distribution, spilling_over, output_video_path))
            conn.commit()

        print("File location of video:", output_video_path)
       

        # Compare user's data with the data in the second database
        second_cursor.execute('SELECT * FROM mlb_hitters WHERE hitting_side = ? AND stance_width = ?', (hitting_side, stance_width))
        mlb_output = second_cursor.fetchone()
        print("MLB output: ", mlb_output)

        if mlb_output:
            # Perform the comparison logic here based on your requirements
            print("User's data:", (hitting_side, stance_width))
            print("Data from the second database:", mlb_output)

            # Print database output
            mlb_output_path = mlb_output[-1]
            print(mlb_output_path)
        
        else:
            print("Error: No data found in the second database.")
            mlb_output_path = None  # Set a default value or handle this case as per your requirement

        print("Output video path:", output_video_path)
        print("MLB output path:", mlb_output_path)

        # Release the VideoWriter
        if out is not None:
            out.release()

        # Release the VideoCapture
        cap.release()

        # Clear the individual frames
        clear_frames(output_directory)
        if spilling_over == "yes":
            print("You're loading too far back. Looking at the pose detection points, the points at the back shoulder, hip, ankle should be close to straight line but should not point away from the body. ")
        
        # Create XML tree
        root = ET.Element("SwingData")

        swing_sections = {}

        # Add swing sections to XML
        for frame_number, section in swing_sections.items():
            frame_element = ET.SubElement(root, "Frame")
            frame_element.set("Number", str(frame_number))
            frame_element.set("Section", section)

        # Create XML file
        tree = ET.ElementTree(root)
        tree.write("swing_data.xml")

        conn.close()
        second_conn.close()

        return output_video_path, mlb_output_path
