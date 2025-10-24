import json
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def load_data(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_data(file_name, data):
    file_path = os.path.join(DATA_DIR, file_name)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
