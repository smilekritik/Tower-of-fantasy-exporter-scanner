import os
import json
import time

directory = "D:\TofMods\Output\Exports\Hotta\Content\Resources"  # Replace with your root folder path

# Clear log.txt at the start of the script
with open('log.txt', 'w', encoding='utf-8') as f:
    pass

def process_json_files(directory):
    unique_attributes = set()  # For storing unique AttributeNames
    attribute_files_map = {}  # For storing AttributeName => file_name
    attribute_to_files = {}  # For storing AttributeName => ModuleExtraType => file_name
    module_extra_to_files = {}  # For storing ModuleExtraType => AttributeName => file_name
    files_read = 0
    files_with_attributes = 0

    # Walk through all subdirectories and files
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_name_only = os.path.basename(filename)
            files_read += 1

            print(f"Reading file: {file_path}")

            if filename.endswith('.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Traverse through the JSON structure to find all "AttributeName" and "ModuleExtraType"
                    found_attributes = False
                    for entry in data:
                        if "Properties" in entry:
                            if "ModuleExtraModifierInfos" in entry["Properties"]:
                                process_attributes(
                                    entry["Properties"]["ModuleExtraModifierInfos"],
                                    file_name_only,
                                    attribute_to_files,
                                    module_extra_to_files,
                                    unique_attributes,
                                    attribute_files_map
                                )
                                found_attributes = True
                            elif "Modifiers" in entry["Properties"]:
                                process_no_module_attributes(
                                    entry["Properties"]["Modifiers"],
                                    file_name_only,
                                    attribute_to_files,
                                    module_extra_to_files,
                                    unique_attributes,
                                    attribute_files_map
                                )
                                found_attributes = True

                    if found_attributes:
                        files_with_attributes += 1

                except json.JSONDecodeError:
                    error_message = f"Error reading {file_path}. Skipping."
                    print(error_message)
                    log_error_to_file(error_message)

    sorted_unique_attributes = sorted(list(unique_attributes))

    return sorted_unique_attributes, attribute_files_map, attribute_to_files, module_extra_to_files, files_read, files_with_attributes


def add_to_mapping(attribute_name, file_name_only, attribute_files_map, attribute_to_files, module_extra_to_files, module_extra_type="NoModule"):
    """
    A helper function to add the attribute to various mappings, handling checks for existing keys and values.
    """
    # Add to unique attribute set and attribute_files_map (AttributeName => [file_name])
    if attribute_name not in attribute_files_map:
        attribute_files_map[attribute_name] = []
    if file_name_only not in attribute_files_map[attribute_name]:
        attribute_files_map[attribute_name].append(file_name_only)

    # Add to attribute_to_files (AttributeName => ModuleExtraType => [file_name])
    if attribute_name not in attribute_to_files:
        attribute_to_files[attribute_name] = {}
    if module_extra_type not in attribute_to_files[attribute_name]:
        attribute_to_files[attribute_name][module_extra_type] = []
    if file_name_only not in attribute_to_files[attribute_name][module_extra_type]:
        attribute_to_files[attribute_name][module_extra_type].append(file_name_only)

    # Add to module_extra_to_files (ModuleExtraType => AttributeName => [file_name])
    if module_extra_type not in module_extra_to_files:
        module_extra_to_files[module_extra_type] = {}
    if attribute_name not in module_extra_to_files[module_extra_type]:
        module_extra_to_files[module_extra_type][attribute_name] = []
    if file_name_only not in module_extra_to_files[module_extra_type][attribute_name]:
        module_extra_to_files[module_extra_type][attribute_name].append(file_name_only)


def process_attributes(module_extra_infos, file_name_only, attribute_to_files, module_extra_to_files, unique_attributes, attribute_files_map):
    for modifier_info in module_extra_infos:
        if "GameplayModifierInfo" in modifier_info and "Attribute" in modifier_info["GameplayModifierInfo"]:
            attribute_info = modifier_info["GameplayModifierInfo"]["Attribute"]

            if "AttributeName" in attribute_info and "ModuleExtraType" in modifier_info:
                attribute_name = attribute_info["AttributeName"]
                module_extra_type = modifier_info["ModuleExtraType"]

                if isinstance(attribute_name, str) and isinstance(module_extra_type, str):
                    unique_attributes.add(attribute_name)
                    add_to_mapping(attribute_name, file_name_only, attribute_files_map, attribute_to_files, module_extra_to_files, module_extra_type)

                    #print(f"Found AttributeName: {attribute_name}, ModuleExtraType: {module_extra_type}")


def process_no_module_attributes(modifiers, file_name_only, attribute_to_files, module_extra_to_files, unique_attributes, attribute_files_map):
    """
    Process attributes that don't have ModuleExtraType and categorize them under 'NoModule'.
    """
    for modifier in modifiers:
        if "Attribute" in modifier and "AttributeName" in modifier["Attribute"]:
            attribute_name = modifier["Attribute"]["AttributeName"]

            if isinstance(attribute_name, str):
                unique_attributes.add(attribute_name)
                add_to_mapping(attribute_name, file_name_only, attribute_files_map, attribute_to_files, module_extra_to_files)

                #print(f"Found NoModule AttributeName: {attribute_name}")


def save_to_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def log_error_to_file(message):
    with open('errorlog.txt', 'a', encoding='utf-8') as f:
        f.write(message + '\n')


def log_summary(start_time, end_time, files_read, unique_attributes_count, files_with_attributes):
    duration = end_time - start_time
    log_message = (
        f"Script started at: {time.ctime(start_time)}\n"
        f"Script ended at: {time.ctime(end_time)}\n"
        f"Time spent: {duration:.2f} seconds\n"
        f"Files read: {files_read}\n"
        f"Unique attributes found: {unique_attributes_count}\n"
        f"Files with attributes found: {files_with_attributes}\n"
    )
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(log_message)


start_time = time.time()
sorted_unique_attributes, attribute_files_map, attribute_to_files, module_extra_to_files, files_read, files_with_attributes = process_json_files(directory)
end_time = time.time()

save_to_json('unique_attributes_sorted.json', sorted_unique_attributes)
save_to_json('attribute_files_map1.json', attribute_files_map)
save_to_json('attribute_to_module_mapping2.json', attribute_to_files)
save_to_json('module_extra_to_files_mapping3.json', module_extra_to_files)


log_summary(start_time, end_time, files_read, len(sorted_unique_attributes), files_with_attributes)
