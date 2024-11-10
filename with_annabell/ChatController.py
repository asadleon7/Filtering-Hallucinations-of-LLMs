import json
import os
import asyncio
import tiktoken
from GeminiController import GeminiController
from QuestionProcessor import TestFileReader
from TextProcessor import TextProcessor
from ToAnnabell import ToAnnabell
from GPTController import GPTController  
from dotenv import load_dotenv
load_dotenv()

class ChatController:
    def __init__(self):
        self.test_file_path = os.getenv("TEST_FILE_PATH")  #File path from .env  
        # Initialize the file reader to read all test questions from the specified path
        self.parsed_links = json.loads(self.test_file_path)
        self.all_content = []
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    # Iterate over each item in the parsed links and read the corresponding file
        for item in self.parsed_links:
            link = item["link"]
            file_range = item["range"]            
            try:
                # Assuming TestFileReader is a class you defined to read files
                file_reader = TestFileReader(link, file_range, "test") # Update the path accordingly
                contents = file_reader.read_file()
                self.all_content.extend(contents)
            except FileNotFoundError:
                print(f"File not found: {link}. Please provide the correct path.")
                exit()
            except Exception as e:
                print(f"An error occurred while reading {link}: {e}")      
        
        # Create an instance of TextProcessor 
        self.text_processor = TextProcessor(self.all_content)
        
        # Initialize the ToAnnabell instance for communication with Annabell
        self.annabell = ToAnnabell()
        
        # Initialize GPTController 
        self.gpt_controller = GPTController()
        
        # Initialize GeminiController 
        self.gemini = GeminiController()
        
        self.stop_repeat = True  # Variable to stop repeating the same questions to Annabell
        #  A golbal variable to store the number of questions asked to Annabell
        self.q = 0
             
    # Method to get the test question that best matches the user's input
    def get_question(self, user_input):
        resulting_sentences = self.text_processor.find_best_match(user_input)
        print("resulting_sentences:", resulting_sentences)
        return resulting_sentences
    
    # Async method to get an answer from Annabell based on the user's input
    async def get_answer_from_annabell(self, user_input):
        q_sentences = self.get_question(user_input) # Get the relevant questions from the test file based on the user input
        question_answer = {}

        if len(q_sentences) >= 1:
            for i, questions in enumerate(q_sentences, 1):
                
                
                # Skip sentences that are already present in the GPT prompts to avoid repetition
                if questions in self.gpt_controller.prompts[0]['content']: # Comment out if-else you want to add all or add  stop_repeat = False
                    print(f"Skipping question: {q_sentences}")
                else:
                    question_key = f"Question {i}"
                    answer_key = f"Answer {i}"
                    question_answer[question_key] = questions
                    print(f"Question {i}: {questions}")
                    # Send the question to Annabell and get the response
                    ann_output = await self.ask_annabell(questions)
                    question_answer[answer_key] = ann_output
                    print(f"Answer {i}: {ann_output}")
        return question_answer

    # Asynchronous method to ask Annabell a question and get the response
    async def ask_annabell(self, sentence):
        # Simulate a response from Annabell by sending the question
        return self.annabell.ask_to_annabell(sentence)
    
    # Asynchronous method to blend the user's input and Annabell's output to get a GPT-3 response
    async def create_prompt(self, sentence):
        # Create and append the user's message to the GPT prompts
        self.gpt_controller.prompts.append(self.gpt_controller.create_user_message(sentence))

        # Get the memory input by asking Annabell the relevant questions
        memory_input = await self.get_answer_from_annabell(sentence)

        # Append memory sentences (questions and answers) to the initial instruction
        if memory_input:
            num_pairs = len(memory_input) // 2  # Calculate the number of question-answer pairs
            for i in range(1, num_pairs + 1):  # Iterate through each pair
                question = memory_input.get(f"Question {i}")
                answer = memory_input.get(f"Answer {i}")
                if question and answer:
                    self.q = self.q + 1
                    self.gpt_controller.prompts[0]['content'] += f", Q.{self.q}. {question},  Ans.{self.q}. {answer}"
                                 
        # Generate the GPT response using the updated prompts
        response = self.gpt_controller.generate_response()
        response_message = response.choices[0].message.content # Extract the response message
        
        # Append the GPT response to the prompts
        self.gpt_controller.prompts.append(self.gpt_controller.create_system_message(response_message))
        # print("Prompt:", self.gpt_controller.prompts)
      # increase the number of prompts to store unique conversation 
      # Max 16385 tokens as per GPT-3 limit after that it will tend to show window context problems
      # within the set limit below system will not ask same question again to Annabell
      # If you want the system to repeat the questions in every user input to Annabell, you can lower the size of prompts 
      # if the limit is reached, the system will start asking the same questions again to Annabell
      # to provide memory to gpt to avoid window context problems
        # print(len(self.gpt_controller.prompts))
        # if len(self.gpt_controller.prompts) > 1000: 
        #     self.stop_repeat = False
        # print("Prompts:", self.gpt_controller.prompts)
       
        # calculate the tokens
        # Extract the 'content' from each message and concatenate them into a single string
        prompt_text = ''.join([message['content'] for message in self.gpt_controller.prompts])
        prompt_tokens = self.encoding.encode(prompt_text)
        print(f"Prompt tokens: {len(prompt_tokens)}")
        response_tokens = self.encoding.encode(response_message)
        print(f"Response tokens: {len(response_tokens)}")
        return response_message

    # Asynchronous method to create a GPT-3 prompt without using Annabell's output
    async def create_prompt_without_annabell(self, sentence):
        # Create and append the user's message to the GPT prompts without Annabell
        self.gpt_controller.prompts_without_annabell.append(self.gpt_controller.create_user_message(sentence))
        
        # Generate the GPT response without including Annabell's output
        response = self.gpt_controller.generate_without_annabell()
        response_message = response.choices[0].message.content
        
        # Append the GPT response to the prompts without Annabell
        self.gpt_controller.prompts_without_annabell.append(self.gpt_controller.create_system_message(response_message))
        
        # Extract the 'content' from each message and concatenate them into a single string
        prompt_text = ''.join([message['content'] for message in self.gpt_controller.prompts_without_annabell])
        prompt_tokens = self.encoding.encode(prompt_text)
        print(f"Prompt tokens: {len(prompt_tokens)}")
        response_tokens = self.encoding.encode(response_message)
        print(f"Prompt tokens: {len(response_tokens)}")
        return response_message
    
    # Asynchronous method to get a response from Gemini
    async def gemini_response(self, user_input):             
        return self.gemini.get_response(user_input)
