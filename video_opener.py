import tkinter as tk
from moviepy.editor import VideoFileClip, clips_array


length = 2

clip1 =VideoFileClip("vid1.MP4").subclip(0, 0 + length).margin(2)
clip2 = VideoFileClip("vid2.MP4").subclip(0, 0 + length).margin(2)

combined = clips_array([[clip1, clip2]])

combined.write_videofile("test.mp4")