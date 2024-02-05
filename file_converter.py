from moviepy.editor import VideoFileClip

def convert_to_mp4(input_file, output_file):
    try:
        video_clip = VideoFileClip(input_file)
        output_file = output_file.split(".")[0] + ".mp4"  # Change the file type to mp4
        video_clip.write_videofile(output_file, codec='libx264', audio=False, threads=4)
        video_clip.reader.close()
        print("Conversion completed successfully.")
        return output_file  # Return the processed MP4 file path
    except KeyError as ke:
        print(f"KeyError during conversion. Details: {str(ke)}")
        return None  # Return None in case of an error
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return None  # Return None in case of an error
