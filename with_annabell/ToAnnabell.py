import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv  

load_dotenv()  # Load environment variables

class ToAnnabell:
    def __init__(self):
        self.write_file = os.getenv("WRITE_FILE_PATH")
        print("Write file:", self.write_file)
        self.read_file = os.getenv("READ_FILE_PATH")
        
        # Initialize the paths for the files used to communicate with Annabell
        self.write_file = self.write_file
        self.read_file = self.read_file
        
        # Set up a file system event handler to monitor changes to the file
        self.event_handler = FileSystemEventHandler()
        self.event_handler.on_modified = self.on_modified
        
        # Initialize the observer to watch the directory containing the files
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path="/home/asad/annabell/annadoc", recursive=False)
        self.observer.start()
        
        # Variable to store Annabell's output
        self.ann_output = None

    # Method to send a new first line to Annabell via the write_file
    def ask_to_annabell(self, new_first_line):
        self.ann_output = None  # Reset the output before each call
        
        # Read all lines from the write_file and replace the first line
        try:
            with open(self.write_file, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            print(f"Error: {self.write_file} not found.")
            return
        except Exception as e:
            print(f"An error occurred while reading {self.write_file}: {e}")
            return

        # Replace the first line with the new input
        if lines:
            lines[0] = new_first_line + '\n'

        # Write the modified lines back to the write_file
        try:
            with open(self.write_file, 'w') as file:
                file.writelines(lines)
        except Exception as e:
            print(f"An error occurred while writing to {self.write_file}: {e}")
            return
        
        # Wait for the file change event that indicates Annabell has responded
        start_time = time.time()
        while self.ann_output is None:
            time.sleep(1)  # Check every second
            if time.time() - start_time > 40:  # Timeout after 40 seconds
                print("Timeout waiting for Annabell's output.")
                return        
        return self.ann_output

    # Event handler for when the read_file is modified
    def on_modified(self, event):
        if event.src_path == self.read_file:
            try:
                # Read the output from Annabell and store it
                with open(self.read_file, 'r') as file:
                    self.ann_output = file.read()
            except FileNotFoundError:
                print(f"Error: {self.read_file} not found.")
            except Exception as e:
                print(f"An error occurred while reading {self.read_file}: {e}")

    # Method to stop the observer when no longer needed
    def stop(self):
        self.observer.stop()
        self.observer.join()
