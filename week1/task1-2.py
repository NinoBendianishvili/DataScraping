import os
import shutil
import csv
import json

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print("FileNotFoundError: File not found.")
    except IOError:
        print("IOError: Unable to read the file.")

def write_file(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(data)
    except IOError:
        print("IOError: Unable to write to the file.")

def append_to_file(file_path, data):
    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(data + '\n')
    except IOError:
        print("IOError: Unable to append to the file.")

def validate_file(file_path):
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return True
    print("FileNotFoundError: File path is not valid or it does not exist.")
    return False

def backup_file(file_path, backup_dir="backup"):
    if validate_file(file_path):
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        backup_path = os.path.join(backup_dir, os.path.basename(file_path))
        shutil.copy(file_path, backup_path)
    else:
        print("Backup failed: Invalid file.")

def parse_csv(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return [row for row in reader]
    except Exception as e:
        print(f"Error reading CSV file. \n Details: {e}")
        return []

def process_json(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"JSONDECODEError: Invalid JSON format. \n details: {e}")
        return {}
    except IOError:
        print("IOError: Unable to read JSON file.")

def filter_data(data, key, value):
    return [item for item in data if item.get(key) == value]

def string_manipulation(text, operation):
    if operation == "lower":
        return text.lower()
    elif operation == "upper":
        return text.upper()
    elif operation == "strip":
        return text.strip()
    else:
        print("Invalid string operation.")
        return text
    

if __name__ == "__main__":
    file_name = "sample.txt"
    write_file(file_name, "Hello, World!")
    print(read_file(file_name))
    append_to_file(file_name, "Appending new line.")
    backup_file(file_name)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "data.csv")
    json_file = os.path.join(script_dir, "data.json")
    print(parse_csv(csv_file))
    print(process_json(json_file))
    
    sample_text = "  Sample Text  "
    print(string_manipulation(sample_text, "strip"))
    print(string_manipulation(sample_text, "lower"))
    print(string_manipulation(sample_text, "upper"))
    print(string_manipulation(sample_text, "invalid"))  