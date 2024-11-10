class TestFileReader:
  
    # Constructor to initialize the file reader with the path, number of files, and file name prefix(test1.txt, test2.txt, ...)
    def __init__(self, file_path, number_of_files, file_name_prefix):
        self.file_path = file_path  # Path where the files are stored
        self.number_of_files = number_of_files  # Number of files to read
        self.file_name_prefix = file_name_prefix  # Prefix of the file names
    
    # Method to read the files and extract all questions
    def read_file(self):
        file_contents = []  # List to store all extracted questions
        
        # Loop through each file based on the number_of_files
        for i in range(1, self.number_of_files + 1):
            # the full file name with path and prefix
            filename = f"{self.file_path}/{self.file_name_prefix}{i}.txt"
            with open(filename, "r") as file:
                contents = file.read()  # Read the entire file contents
                # Split the contents by line and filter lines containing a question
                for line in contents.split("\n"): 
                    if "?" in line and all(char not in line for char in ["/", "*", "."]):
                        # Remove the leading '#' if present before the question
                        cleaned_line = line.lstrip('#')
                        file_contents.append(cleaned_line)  # Add the cleaned question to the list
        
        return file_contents  # Return the list of extracted questions
