from pytube import YouTube

def download_video(url, output_path= "C:\SeniorDesign\mlb_hitters"):
    try:
        # Create a YouTube object
        yt = YouTube(url)

        # Get the highest resolution stream
        video_stream = yt.streams.get_highest_resolution()

        # Download the video
        print(f"Downloading: {yt.title}...")
        video_stream.download(output_path)
        print("Download complete!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Get the YouTube video URL from the user
    video_url = input("Enter the YouTube video URL: ")

    # Specify the output path (current directory by default)
    output_path = input("Enter the output path (press Enter for current directory): ").strip()

    # Download the video
    download_video(video_url, output_path)
