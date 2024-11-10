import os
import re
from functools import reduce
from dotenv import load_dotenv

# Load environment variables 
load_dotenv() 

class AnnabellKnowledge:
    def __init__(self):
        # Get the file path from the env
        self.file_path = os.getenv("KNOWLEDGE_PATH")
        
    # text cleaning function
    def clean_line(self, line):
        # List of (pattern, replacement) tuples
        patterns_replacements = [
            (r'\s*-\s*', ''),                       
            (r'\b(\w+)-s\b', r'\1s'),               
            (r'\b(\w+)-es\b', r'\1es'),             
            (r'\b(\w+)-ing\b', r'\1ing'),            
            (r"\b(\w+)\s*'s\b", r"\1's"),            
            (r'(\w+)_(\w+)', r'\1-\2')               
        ]
        
        # The re.sub patterns in one line using reduce
        line = reduce(lambda text, pattern_repl: re.sub(pattern_repl[0], pattern_repl[1], text), patterns_replacements, line)
        
        # Replace underscores 
        line = line.replace("_", " ")
        
        # Strip any leading/trailing whitespace
        return line.strip()
    
    def get_data(self):
        # Read the file and process each line
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            print("File not found. Please provide the correct path.")
            return []
        # Apply the cleaning 
        cleaned_lines = [self.clean_line(line) for line in lines]

        # Join all lines into a single string 
        prompt = "\n".join(cleaned_lines)

        # return the processed text
        return prompt
        

