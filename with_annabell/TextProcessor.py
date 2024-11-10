
import os
import json
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import numpy as np
from QuestionProcessor import TestFileReader

load_dotenv()

class TextProcessor:
    def __init__(self, file_content):
        # Store the list of sentences to match against
        self.all_content = file_content
        # Remove duplicate sentences
        self.text_file_contents = list(set(self.all_content))
        # Store sentences and scores
        self.sentence_scores = {}
        
    def find_best_match(self, user_input):
        # Clear previous sentence scores
        self.sentence_scores.clear()
                
        documents = [user_input] + self.text_file_contents 
        vectorizer = TfidfVectorizer(stop_words='english')  # initialize TF-IDF vectorizer
        tfidf_matrix = vectorizer.fit_transform(documents)  # create TF-IDF matrix
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()  # compute cosine similarities
        max_score = np.max(cosine_similarities)  # find the maximum similarity score
        # Store all sentences with their corresponding similarity scores in a dictionary
        all_sentence_scores = {content: score for content, score in zip(self.text_file_contents, cosine_similarities)}
        # Filter out sentences with a score of 0
        filtered_sentence_scores = {content: score for content, score in all_sentence_scores.items() if score > 0}
        
        # Sort the remaining sentences by their similarity scores in descending order and keep the top 5
        top_five_sentences = dict(sorted(filtered_sentence_scores.items(), key=lambda item: item[1], reverse=True)[:3])
        
        # Store the top five sentences in self.sentence_scores
        self.sentence_scores.update(top_five_sentences)
        
        # Extract the top five sentences without the scores
        top_sentences = list(top_five_sentences.keys())
        
        # Return the list of top five sentences
        return top_sentences if top_sentences else []

        # Gather all sentences with the maximum score
        # if max_score > 0:
        #     top_matches = [content for content, score in zip(self.text_file_contents, cosine_similarities) if score == max_score]
        #     print(f"Top similarity score: {max_score:.4f}")                       
        #     return top_matches
        # else:
        # print("No meaningful match found.")
        # return []  # Return an empty list if no match found
    
    # method to write the sentence scores to a file    
    def get_sentence_scores(self, file_path, user_input):
                
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # If the file is empty, write the header
            if file.tell() == 0:
                writer.writerow(['User Input','Sentence', 'Score'])
           
            # Write the dataCCEE Demo
            for sentence, score in self.sentence_scores.items():
                writer.writerow([user_input, sentence, score])
        
        return self.sentence_scores

# Test use and data collection for the sentence scores
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

    # Now, `all_content` should be a flat list of unique strings
    # print(all_content)     
    text_processor = TextProcessor(all_content)
    # Write all contents to a file
    # output_file_path = "all_questions.txt"  # Specify the path where you want to save the content
    # with open(output_file_path, "w") as output_file:
    #     for content in all_content:
    #         output_file.write(content + "\n")  
    while True:
        # Get user input
        user_input = input("You: ")

        # Break the loop with exit
        if user_input.lower() == 'exit':
            break

        # Process the user input
        best_match_sentences = text_processor.find_best_match(user_input)
        if best_match_sentences:
            for sentence in best_match_sentences:
                print("Top scored sentence:", sentence)
        else:
            print("No match found.")
            
        print("Sentence scores:")
        print(text_processor.get_sentence_scores("data_collection/Tfidfvector_scores.csv", user_input))