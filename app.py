import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from moviepy.editor import VideoFileClip
from moviepy.editor import clips_array
from user_input import hitter_analysis
from mlb_db_code import open_mlb_db
import cv2
import os

def select_video_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.mov")])
    return file_path

def get_next_video_name(output_directory, base_name):
    output_directory = r"C:\SeniorDesign\final_op"
    existing_videos = [f for f in os.listdir(output_directory) if f.endswith(".mp4")]
    index = 1
    while True:
        video_name = f"{base_name}{index}.mp4"
        if video_name in existing_videos:
            index += 1
        else:
            return os.path.join(output_directory, video_name)
def combine_videos():
    length = 120

    vid1_path = select_video_file()
    if not vid1_path:
        print("No file selected for the first video.")
        return

    vid2_path = select_video_file()
    if not vid2_path:
        print("No file selected for the second video.")
        return

    clip1 = VideoFileClip(vid1_path)
    clip2 = VideoFileClip(vid2_path)

    combined = clips_array([[clip1, clip2]])
    combined.write_videofile("combined.mp4")

def combine_videos1(output_video_path, mlb_video_path):
    base_name = "final_op"
    output_directory = r"C:\SeniorDesign\final_op"
    combined_video_name = get_next_video_name(output_directory, base_name)
    combined_video_path = os.path.join(output_directory, combined_video_name)
    length = 60

    video1 = VideoFileClip(output_video_path)
    video2 = VideoFileClip(mlb_video_path)

    # Resize videos to have the same height
    min_height = min(video1.h, video2.h)
    video1 = video1.resize(height=min_height)
    video2 = video2.resize(height=min_height)

    # Create side-by-side array of clips
    combined_video = clips_array([[video1, video2]])

    # Write the combined video to a file
    
    combined_video.write_videofile(combined_video_path)

    return combined_video_path


def option_selected():
    selected_option = option_var.get()
    if selected_option == "User Database":
        def convert_to_mp4(input_file):
            try:
                # Generate the output file path by replacing the file extension with .mp4
                output_file = input_file.rsplit('.', 1)[0] + ".mp4"
                video_clip = VideoFileClip(input_file)
                video_clip.write_videofile(output_file, codec='libx264', threads=4)
                print(f"Conversion completed successfully. Output file: {output_file}")
            except Exception as e:
                print(f"Error: {str(e)}")

        input_file = select_video_file()  # Use the select_video_file function to choose the input file
        if input_file:  # Check if a file was selected
            convert_to_mp4(input_file)
        else:
            print("No file selected.")
        print("User Database selected")

    elif selected_option == "Hitter Analysis":
        print("Hitter Analysis selected")
        output_video_path, mlb_output_path = hitter_analysis()

        if output_video_path and mlb_output_path:
            combined_video_path = combine_videos1(output_video_path, mlb_output_path)
            print("Combined video path:", combined_video_path)
            return combined_video_path, mlb_output_path
        else:
            print("Error: One or both video paths are missing.")
            return None, None
    
    elif selected_option == "Professional Database":
        print("Professional database selected")
        open_mlb_db()
    elif selected_option == "Combine":
        combine_videos()
        print("Combine video selected")


# Create the main window
root = tk.Tk()
root.title("GUI with Options")

# Load and display the image
image = Image.open(r"C:\Users\Carson\Pictures\soto.jpg")  # Insert the path to your image
photo = ImageTk.PhotoImage(image)
image_label = tk.Label(root, image=photo)
image_label.pack()

# Create a frame for the options
options_frame = ttk.Frame(root)
options_frame.pack(pady=10)

# Create the options
options = ["User Database", "Hitter Analysis", "Professional Database", "Combine"]
option_var = tk.StringVar()
option_var.set(options[0])

for option in options:
    ttk.Radiobutton(options_frame, text=option, variable=option_var, value=option).pack(side="left")

# Create a button to trigger the selected option
select_button = ttk.Button(root, text="Select", command=option_selected)
select_button.pack(pady=10)

root.mainloop()
