import json
import os

def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None

data_new = load_json('Exported/module_extra_to_files_mapping3.json')
data_old = load_json('Exported/module_extra_to_files_mapping3_old.json')

def find_new_elements(d1, d2):
    diff = {}
    for key in d1.keys() | d2.keys():
        if isinstance(d1.get(key), list) and isinstance(d2.get(key), list):
            old_list = d2.get(key, [])
            new_list = d1.get(key, [])
            added = [item for item in new_list if item not in old_list]
            if added:
                diff[key] = added
        elif isinstance(d1.get(key), dict) and isinstance(d2.get(key), dict):
            nested_diff = find_new_elements(d1[key], d2[key])
            if nested_diff:
                diff[key] = nested_diff
    return diff

def save_to_json(filename, data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if data_new is not None and data_old is not None:
    new_elements = find_new_elements(data_new, data_old)
    output_filename = 'Exported/difference_4.3.json'
    save_to_json(output_filename, new_elements)
    print(f"Difference saved to {output_filename}")
else:
    print("Error: One or both JSON files could not be loaded.")
