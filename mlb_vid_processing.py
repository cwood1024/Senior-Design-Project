import cv2
import mediapipe as mp
import os
from datetime import datetime
from prettytable import PrettyTable
import sqlite3
import numpy as np


def get_next_video_name(output_directory, base_name):
    # Use the current timestamp to make the video name unique
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    video_name = f"{base_name}_{timestamp}.mp4"
    return os.path.join(output_directory, video_name)

def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def print_database_output(cursor):
    # Fetch all data from the database
    cursor.execute('SELECT * FROM mlb_hitters')
    hitters_data = cursor.fetchall()

    # Create a PrettyTable instance and add columns
    table = PrettyTable()
    table.field_names = ["ID", "Hitter Name", "Hitting Side", "Stance Width", "Weight Distribution", "Spilling Over", "Video Location"]

    # Add data to the table
    for row in hitters_data:
        table.add_row(row)
    print(table)

def process_hitter_video():
    video_path = input("Enter the path to the video file: ")
    output_directory = r"C:\SeniorDesign\mlb_hitters_processed"
    hitter_name = input("Enter the hitter's name: ")

    # Database code       
    conn = sqlite3.connect('mlb_hitters_data.db')
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS mlb_hitters (
                id INTEGER PRIMARY KEY,
                hitter_name TEXT,
                hitting_side TEXT, 
                stance_width TEXT,
                weight_distribution TEXT,
                spilling_over TEXT,
                video_location TEXT   
            )
        ''')
    conn.commit()

    stance_width = ""
    hitting_side = ""

    output_path = get_next_video_name(output_directory, "mlb_output")

    # Initialize MediaPipe Pose and Drawing utilities
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose()

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get video properties (width, height, fps)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 120

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if out.isOpened():
        print("Output video file has been created")

    frame_number = 0
    max_frame_count = 5

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        print("Processing frame:",f"frame_{frame_number:04d}.jpg")
        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe Pose
        result = pose.process(frame_rgb)
        
        if result.pose_landmarks is not None:
                                
                left_arm_landmarks = [result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER],
                                        result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW],
                                        result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]]
                right_arm_landmarks = [result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER],
                                        result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW],
                                        result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]]
                left_leg_landmarks = [result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP],
                                        result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE],
                                        result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]]
                right_leg_landmarks = [result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP],
                                        result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE],
                                        result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]]
                head_landmark = result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
                
                if result.pose_landmarks and frame_number < max_frame_count:
            # Your classification logic here
                    knee_distance = abs(result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].x - result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].x)
                    shoulder_distance = abs(result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x - result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x)
                
                    if abs(result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x > result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x):
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
                landmarks = result.pose_landmarks.landmark
                hip = (landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y)
                knee = (landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x ,
                        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y )
                ankle = (landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x ,
                        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y )
                # Analyze alignment - stack the back side
                back_line = np.array([hip, knee, ankle])
                alignment_error = np.linalg.norm(np.cross(back_line[1] - back_line[0], back_line[0] - back_line[2])) / np.linalg.norm(back_line[1] - back_line[0])

                # Check for hip hinge
                hip_hinge = calculate_angle(hip, knee, ankle)

                # Check weight distribution
                weight_distribution = 'balanced' if hip_hinge < 85 else 'over'

                # Assess spilling over
                spilling_over = 'yes' if hip_hinge > 90 else 'no'
        # Draw the pose landmarks on the frame
        if result.pose_landmarks:
            mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        frame_number += 1
        if out is None:
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        out.write(frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Insert data into the database, including the video location
    cursor.execute('''
        INSERT INTO mlb_hitters (hitter_name, hitting_side, stance_width, weight_distribution, spilling_over, video_location)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (hitter_name, hitting_side, stance_width, weight_distribution, spilling_over, output_path))
    conn.commit()
        
    print(f"Video has been saved to: {output_path}")

    # Print database output
    cursor.execute('SELECT * FROM mlb_hitters')
    hitters_data = cursor.fetchall()

    print("Hitters data:")
    print_database_output(cursor)


    out.release()
    cap.release()
    cv2.destroyAllWindows()


