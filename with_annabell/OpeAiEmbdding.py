
# It is a standalone file to get the contextually similar sentence from the text file with user input.
# This is OpenAI Embedding based text processor.
# Details: https://platform.openai.com/docs/guides/embeddings/what-are-embeddings
# and find the best matching sentences based on cosine similarity between embeddings.

import os
from openai import OpenAI
import csv
import json
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from QuestionProcessor import TestFileReader

load_dotenv()

# Load environment variables from a .env file (if using)
load_dotenv()


class TextProcessor:
    def __init__(self, file_content):
        self.text_file_contents = file_content
        self.sentence_scores = {}  # Store sentences and scores
        self.embeddings_cache = {}  # Cache embeddings to avoid recomputation
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.embeddings_file='embeddings_cache.json'
        
        # Load embeddings from file if it exists
        if os.path.exists(self.embeddings_file):
            with open(self.embeddings_file, 'r') as f:
                self.embeddings_cache = json.load(f)
        
    def save_embeddings(self):
        # Save embeddings to file
        with open(self.embeddings_file, 'w') as f:
            json.dump(self.embeddings_cache, f)
            
    def get_embedding(self, text):
        # Check if embedding is already cached
        if text in self.embeddings_cache:
            return np.array(self.embeddings_cache[text])
        
        # Get embedding from OpenAI API
        response = self.client.embeddings.create(
            input=[text],
            model="text-embedding-ada-002"
        )
       
        embedding = np.array(response.data[0].embedding)
        print("Embedding ",embedding)
        # Cache the embedding
        self.embeddings_cache[text] = embedding.tolist()
        self.save_embeddings()
        
        return embedding
    
    def find_best_match(self, user_input):
        self.sentence_scores.clear()  # Clear previous sentence scores
        
        input_embedding = self.get_embedding(user_input)  # Get embedding for user input
        content_embeddings = [self.get_embedding(content) for content in self.text_file_contents]  # Get embeddings for stored sentences
        
        # Compute cosine similarities between the input and all stored sentences
        similarities = [cosine_similarity([input_embedding], [content_embedding]).flatten()[0] for content_embedding in content_embeddings]
        max_score = np.max(similarities)  # Find the maximum similarity score
           # Store all sentences with their corresponding similarity scores in a dictionary
        all_sentence_scores = {content: score for content, score in zip(self.text_file_contents, similarities)}
        
        # Sort sentences by their similarity scores in descending order and keep the top 5
        top_five_sentences = dict(sorted(all_sentence_scores.items(), key=lambda item: item[1], reverse=True)[:5])
        
        # Store the top five sentences in self.sentence_scores
        self.sentence_scores.update(top_five_sentences)  
        print("Top Five sentence scores ", self.sentence_scores)  
        
        # Gather all sentences with the maximum score
        if max_score > 0:
            top_matches = [content for content, score in zip(self.text_file_contents, similarities) if score == max_score]
            print(f"Top similarity score: {max_score:.4f}")
            
            for sentence in top_matches:
                print(f"- {sentence}")
         
           
            return top_matches
        else:
            print("No meaningful match found.")
            return []  # Return an empty list if no match found
    
    def get_sentence_scores(self, file_path, user_input): # method to write the top 5 sentence scores to a file 
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # If the file is empty, write the header
            if file.tell() == 0:
                writer.writerow(['User Input', 'Sentence', 'Score'])
            
            # Write the data
            for sentence, score in self.sentence_scores.items():
                writer.writerow([user_input, sentence, score])
        
        return self.sentence_scores

# Test use
if __name__ == "__main__":
    
    test_file_path = os.getenv("TEST_FILE_PATH")    
    parsed_links = json.loads(test_file_path)
    all_content = []
    # Iterate over each item in the parsed links and read the corresponding file
    for item in parsed_links:
        link = item["link"]
        file_range = item["range"]
        
        try:
            # Assuming TestFileReader is a class you defined to read files
            file_reader = TestFileReader(link, file_range, "test") # Update the path accordingly
            contents = file_reader.read_file()
            all_content.extend(contents)
        except FileNotFoundError:
            print(f"File not found: {link}. Please provide the correct path.")
            exit()
        except Exception as e:
            print(f"An error occurred while reading {link}: {e}")
    # Remove duplicate sentences
    all_content = list(set(all_content))
    
    text_processor = TextProcessor(all_content)

    while True:
        # Get user input
        user_input = input("You: ")

        # Break the loop with exit
        if user_input.lower() == 'exit':
            break

        # Process the user input
        best_match_sentences = text_processor.find_best_match(user_input)
        if best_match_sentences:
            print("Best Match Sentences:")
            for sentence in best_match_sentences:
                print(f"- {sentence}")
        else:
            print("No match found.")
        #Print and write the sentence scores to a file
        print(text_processor.get_sentence_scores("data_collection/semantic_scores.csv", user_input))
