import os
import json


"""
If you want to run this file again, delete all the content from the file train_set.jsonl.
The script appends data to the file, it doesn't overwrite it.
"""


# Reading from the csv (not really csv) file and appends them to the .jsonl file
def read_from_csv(file_name):
    with open(file_name, 'r') as file:
        line_count = 0
        lines = file.readlines()
        for line in lines:
            if line_count == 0:
                line_count += 1
                continue
            item = {
                "messages": [
                    {"role": "system", "content": "Chessbot is a factual chatbot that can explain the rules of chess"},
                    {"role": "user", "content": line.split('?,')[0] + "?"},
                    {"role": "assistant", "content": line.split('?,')[1].strip()}]
            }
            with open('Training_sets/train_set.jsonl', 'a') as writer:
                writer.write(json.dumps(item) + "\n")
            line_count += 1


# Goes through all the files from the Training_sets directory
def iterate_through_directory():
    for file in os.listdir('Training_sets'):
        read_from_csv(os.path.join('Training_sets', file))


iterate_through_directory()
