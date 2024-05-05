from moviepy.editor import VideoFileClip

def convert_to_mp4(input_file, output_file, output_resolution=None):
    try:
        video_clip = VideoFileClip(input_file)

        if output_resolution:
            video_clip = video_clip.resize(output_resolution)

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

if __name__ == "__main__":
    # Provide the input and output file paths
    input_file_path = r"c:\SeniorDesign\hitting_input_vids_clipped\IMG_1664.mov"
    output_file_path = "output_video.mp4"  # Replace with your desired output video file path
    output_resolution = (1080, 1920)  # Replace with your desired output resolution, e.g., (width, height)

    # Call the convert_to_mp4 function with the specified output resolution
    result = convert_to_mp4(input_file_path, output_file_path, output_resolution)

    # Check the result and take further actions if needed
    if result is not None:
        print(f"Conversion successful. Output video saved at: {result}")
    else:
        print("Conversion failed. Please check the error messages for details.")
