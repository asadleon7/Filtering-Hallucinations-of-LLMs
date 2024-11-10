import os
from openai import OpenAI
from dotenv import load_dotenv
from AnnabellKnowledge import AnnabellKnowledge
# Load environment variables from .env file
load_dotenv()

class GPTController:
    def __init__(self):
        # Initialize OpenAI client for interacting with GPT models
        self.GPT_MODEL = "gpt-3.5-turbo"  # Specify the GPT model 
        # Retrieve the OpenAI API key from the environment
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        try:
            self.client = OpenAI(api_key=api_key)  # Create an instance of the OpenAI client with the API key
        except Exception as e:
            print(f"Failed to initialize OpenAI client: {e}")
            raise
              
        self.annabel_knowledge = AnnabellKnowledge() # Initialize the knowledge of Annabell
        # Initialize the system message for conversations involving Annabell
        self.prompts = [
            self.create_system_message(
                'Before answering you must read the whole content. The question answer set is your background knowledge. Your name is Annabell. Act and answer like a four years girl. You may greet the person. You may have personal choices, beliefs, relations, and opinions or other characters that humans can have or do.'
            )
        ]
        
        # Initialize the system message for conversations without Annabell
        knowledge = self.annabel_knowledge.get_data() # Get the knowledge  from Annabell's data set
        
        self.prompts_without_annabell = [
            self.create_system_message(
                'Consider you are Annabell, Act and answer like a four years girl.. You will greet the person by asking their name. You may have personal choices, beliefs, relations, and opinions or other characters that humans can have. below texts are your knowledge \n' + knowledge
            )
        ]
    
    # Method to create a user message for the conversation
    def create_user_message(self, user_input):
        return {"role": "user", "content": user_input}
    
    # Method to create a system message for the conversation
    def create_system_message(self, content):
        return {"role": "system", "content": content}
    
    # Method to generate a response from GPT with Annabell's context
    def generate_response(self):
        # Send the list of messages (prompts) to the GPT model and get the AI's response
        try:
            response = self.client.chat.completions.create(
                model=self.GPT_MODEL,  # Specify the model to use
                messages=self.prompts,  
                max_tokens=100,  # The maximum number of tokens to generate
                temperature=0.85  # Control the creativity of the response (higher = more creative)
            )
            return response
        except Exception as e:  
            print(e)
            return None
        
    # reset the prompts
    def reset_prompts(self):
        self.prompts = [
            self.create_system_message(
                'Before answering you must read the whole content. Consider the question answer as your background knowledge. Consider you are Annabell, acts like human. You will greet the person by asking their name. You may have personal choices, beliefs, relations, and opinions or other characters that humans can have.'
            )
        ]
        
    # Method to generate a response from GPT without Annabell's context
    def generate_without_annabell(self):
        # Send the list of messages (prompts without Annabell's context) to the GPT model and get the AI's response
       try:
            response = self.client.chat.completions.create(
                model=self.GPT_MODEL,  # Specify the model to use
                messages=self.prompts_without_annabell,  
                max_tokens=100,  # The maximum number of tokens to generate
                temperature=1  # Control the creativity of the response (higher = more creative)
            )
            return response
       except Exception as e:  
            print(e)
            return None
   
