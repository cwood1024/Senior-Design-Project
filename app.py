import tkinter as tk
from user_input import hitter_analysis
from mlb_db_code import open_mlb_db
from moviepy.editor import VideoFileClip, clips_array
import cv2


mlb_output_path = None
class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Baseball Analysis App")
        self.root.configure(bg='light blue')  # Set background color to black

        # Center the window on the screen
        self.center_window()

        # Analysis menu
        analysis_menu = tk.Frame(self.root, bg='light blue')
        analysis_menu.grid(row=0, column=0)

        # Add menu items with grid geometry manager
        menu_items = ["Hitter Analysis", "User Database", "MLB Database", "App Info"]

        for index, item in enumerate(menu_items):
            button = tk.Button(analysis_menu, text=item, command=lambda i=item: self.open_window(i), bg='white', fg='black')
            button.grid(row=0, column=index, padx=10, pady=10)

        # Bind the resize event to center the window
        self.root.bind("<Configure>", self.center_window)

    def center_window(self, event=None):
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate x and y coordinates for the center of the screen
        x = (screen_width - self.root.winfo_reqwidth()) / 2
        y = (screen_height - self.root.winfo_reqheight()) / 2

        # Set the position of the window
        self.root.geometry("+%d+%d" % (x, y))

    def open_window(self, title):
        if title == "Hitter Analysis":
            self.run_hitter_analysis_code()
        elif title == "MLB Database":
            self.run_mlb_database_code()
        else:
            new_window = tk.Toplevel(self.root)
            new_window.title(title)
            label = tk.Label(new_window, text=f"This is the {title} window.")
            label.pack(padx=20, pady=20)


    def run_hitter_analysis_code(self):  
        
        result_video_path, mlb_db_output = hitter_analysis()

        def display_side_by_side(result_video_path, mlb_output_path):
            cap1 = cv2.VideoCapture(result_video_path)
            cap2 = cv2.VideoCapture(mlb_output_path)

            while cap1.isOpened() and cap2.isOpened():
                ret1, frame1 = cap1.read()
                ret2, frame2 = cap2.read()

                if not ret1 or not ret2:
                    break

                # Resize frames if necessary
                frame1 = cv2.resize(frame1, (640, 480))
                frame2 = cv2.resize(frame2, (640, 480))

                # Display frames side by side
                display_frame = cv2.hconcat([frame1, frame2])
                cv2.imshow("Side-by-Side Display", display_frame)

                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break

            cap1.release()
            cap2.release()
            cv2.destroyAllWindows()

        display_side_by_side(result_video_path, mlb_output_path)

        '''
        length = 30

        clip1 =VideoFileClip(result_video_path).subclip(0, 0 + length).margin(2)
        clip2 = VideoFileClip(mlb_db_output).subclip(0, 0 + length).margin(2)

        combined = clips_array([[clip1, clip2]])

        combined.write_videofile("Processed Video")'''
        
    def run_mlb_database_code(self):
        open_mlb_db()

def main():
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()