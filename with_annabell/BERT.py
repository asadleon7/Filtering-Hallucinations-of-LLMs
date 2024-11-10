# This file is not integreted with the other files. 
# It is a standalone file to get the contextually similar sentence from the text file with user input.
# This is BERT (Bidirectional Encoder Representations from Transformers) based text processor. 
# It uses the Hugging Face Transformers library to encode sentences into BERT embeddings 
# and find the best matching sentences based on cosine similarity between embeddings.
# require pip install transformers torch

import csv
import os 
import torch
import json
import numpy as np
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from QuestionProcessor import TestFileReader

load_dotenv() # Load environment variables

class TransformerTextProcessor:
    def __init__(self, file_content):
        self.text_file_contents = file_content
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.sentence_scores = {} # store sentences and scores
        
    def encode_sentence(self, sentence):
        # Encodes a sentence into BERT
        inputs = self.tokenizer(sentence, return_tensors='pt', truncation=True, max_length=512, padding=True)
        
        outputs = self.model(**inputs)
        # Use the [CLS] token's embedding 
        sentence_embedding = outputs.last_hidden_state[:, 0, :].detach().numpy()
        return sentence_embedding

        # Finds the best matching sentences using BERT embeddings.
    def find_best_match(self, user_input):
        self.sentence_scores.clear()  # Clear previous sentence scores
        input_embedding = self.encode_sentence(user_input)  # Encode the user input
        content_embeddings = [self.encode_sentence(content) for content in self.text_file_contents]  # Encode all stored sentences
        
        # Compute cosine similarities between the input and all stored sentences
        similarities = [cosine_similarity(input_embedding, content_embedding).flatten()[0] for content_embedding in content_embeddings]
        max_score = np.max(similarities)  # Find the maximum similarity score
        
         # Store all similar sentences with their scores in a dictionary
        all_sentence_scores = {content: score for content, score in zip(self.text_file_contents, similarities)}
        
        # Sort sentences by their similarity scores in descending order and keep the top 5
        top_five_sentences = dict(sorted(all_sentence_scores.items(), key=lambda item: item[1], reverse=True)[:5])
        
        # Store the top five sentences in self.sentence_scores
        self.sentence_scores.update(top_five_sentences)  
          
        # Gather all sentences with the maximum score
        if max_score > 0:
            top_matches = [content for content, score in zip(self.text_file_contents, similarities) if score == max_score]
            print(f"Top similarity score: {max_score:.4f}")
            print("Sentences with the top similarity score:")
            for sentence in top_matches:
                print(f"- {sentence}")
            
            
            return top_matches
        else:
            print("No meaningful match found.")
            return []  # Return an empty list if no match found
        
# method to wrtie the sentence scores to a file
    def get_sentence_scores(self, file_path, user_input):
                
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # If the file is empty, write the header
            if file.tell() == 0:
                writer.writerow(['User Input','Sentence', 'Score'])
           
            # Write the data
            for sentence, score in self.sentence_scores.items():
                writer.writerow([user_input, sentence, score])
        
        return self.sentence_scores

# Test use
# example question - Who is Oliver?
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
   
    text_processor = TransformerTextProcessor(all_content)

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
        # Print and write the sentence scores to a file 
        print(text_processor.get_sentence_scores("data_collection/bert_scores.csv", user_input))