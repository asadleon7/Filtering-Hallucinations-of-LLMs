import os
import google.generativeai as genai
from AnnabellKnowledge import AnnabellKnowledge
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GeminiController:
    def __init__(self):
      
        # Retrieve the Google API key from the environment
        api_key = os.getenv("API_KEY")
        
        if not api_key:
            raise ValueError("Google API key not found. Please set the API_KEY environment variable.")
        
        try:
            genai.configure(api_key=api_key)  # Configure the Google Generative AI client with the API key
        except Exception as e:
            print(f"Failed to configure Google Generative AI client: {e}")
            raise 
                
        # Initialize the generative model with the specified version
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.annabel_knowledge = AnnabellKnowledge() 
        knowledge = self.annabel_knowledge.get_data()
        # Define the initial conversation background with a greeting from the user and a response from the model
        self.background = [
            {"role": "user", 
             "parts": f"Hello! Consider you are Annabell, Act and answer like a four years girl, you can have personal choice, belief and relations. You have this information about you: \n{knowledge} "},
            {"role": "model", 
             "parts": "Great to meet you. What would you like to know? "},
        ]

        # Start the chat session with the initial background conversation history
        self.chat = self.model.start_chat(history=self.background)
        
       
    
    # Method to get a response from the model based on the user's input
    def get_response(self, user_input):
        response = self.chat.send_message(user_input)  # Send the user's input to the model and get the response
        return response.text  # Return the text of the model's response

# Testing the GeminiController class
if __name__ == "__main__":
    chat = GeminiController()  # Instantiate the GeminiController class

    while True:
        # Get user input from the console
        user_input = input("You: ")
        
        # Break the loop if the user types 'exit'
        if user_input.lower() == 'exit':
            break

        # Get and print the response from the model based on the user input
        response = chat.get_response(user_input)
        print("Gemini response:", response)
