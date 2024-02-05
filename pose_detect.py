# pose_detection.py
import mediapipe as mp
import cv2

def detect_pose(image):
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    with mp_pose.Pose(static_image_mode=True) as pose:
        results_pose = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Draw pose landmarks
        annotated_image = image.copy()
        if results_pose.pose_landmarks is not None:
            mp_drawing.draw_landmarks(annotated_image, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Label the body parts
        left_arm_landmarks = []
        left_leg_landmarks = []
        right_arm_landmarks = []
        right_leg_landmarks = []
        head_landmarks = []

        stance_width = ""
        hitting_side = ""
        
        if results_pose.pose_landmarks is not None:
                            
            left_arm_landmarks = [results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER],
                                    results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW],
                                    results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]]
            right_arm_landmarks = [results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER],
                                    results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW],
                                    results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]]
            left_leg_landmarks = [results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP],
                                    results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE],
                                    results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]]
            right_leg_landmarks = [results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP],
                                    results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE],
                                    results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]]
            head_landmark = results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            # Label the left arm
            for idx, landmark in enumerate(left_arm_landmarks):
                if landmark is not None:
                    cv2.putText(annotated_image, f'Left Arm {idx}', (int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                else:
                    print("Left arm landmark not found.")
                    default_position = (100, 100)  # Example default position
                    cv2.putText(annotated_image, f'Left Arm {idx}', default_position,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

            # Label the right arm
            for idx, landmark in enumerate(right_arm_landmarks):
                if landmark is not None:
                    cv2.putText(annotated_image, f'Right Arm {idx}', (int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                else:
                    print("Right arm landmark not found.")
                
            # Label the left leg
            for idx, landmark in enumerate(left_leg_landmarks):
                if landmark is not None:
                    cv2.putText(annotated_image, f'Left Leg {idx}', (int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                else:
                    print("Left leg landmark not found.")
                
            # Label the right leg
            for idx, landmark in enumerate(right_leg_landmarks):
                if landmark is not None:
                    cv2.putText(annotated_image, f'Right Leg {idx}', (int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                else:
                    print("Left leg landmark not found.")
            
           #Label the head
            for idx, landmark in enumerate(head_landmarks):
                if landmark is not None:
                    head_x = int(landmark.x * image.shape[1])
                    head_y = int(landmark.y * image.shape[0])
                    cv2.putText(annotated_image, 'Head', (head_x, head_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                else:
                    print("Head landmark not found")

        else:  
            print("Pose landmarks not found")
            
    return results_pose
