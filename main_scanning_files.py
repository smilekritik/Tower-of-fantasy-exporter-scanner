import os
import json
import time

directory = r"D:\TofMods\Exporter\some"  # Replace with your root folder path

# Ensure the logs directory exists
LOGS_DIR = 'Logs'
os.makedirs(LOGS_DIR, exist_ok=True)

# Log file paths
LOG_EMPTY_FILES = os.path.join(LOGS_DIR, 'log_empty_files.txt')
LOG_PROCESSED_FILES = os.path.join(LOGS_DIR, 'log_processed_files.txt')
LOG_SCANNED_FILES = os.path.join(LOGS_DIR, 'log_scanned_files.txt')
LOG_INFO = os.path.join(LOGS_DIR, 'log_info.txt')

# Clear log_info.txt at the start of the script
with open(LOG_INFO, 'w', encoding='utf-8') as f:
    pass

def initialize_logs():
    """
    Ensure log files exist and initialize them if they don't.
    """
    for log_file in [LOG_EMPTY_FILES, LOG_PROCESSED_FILES, LOG_SCANNED_FILES]:
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                pass

def read_log_file(log_file):
    """
    Read a log file and return a set of entries.
    """
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def write_to_log_file(log_file, entries, overwrite=False):
    """
    Write a set of entries to a log file.
    If overwrite is True, the file will be overwritten with the new entries.
    """
    mode = 'w' if overwrite else 'a'
    with open(log_file, mode, encoding='utf-8') as f:
        for entry in sorted(entries):  # Sort entries for consistency
            f.write(entry + '\n')

def process_json_files(directory, mode):
    unique_attributes = set()  # For storing unique AttributeNames
    attribute_files_map = {}  # For storing AttributeName => file_name
    attribute_to_files = {}  # For storing AttributeName => ModuleExtraType => file_name
    module_extra_to_files = {}  # For storing ModuleExtraType => AttributeName => file_name
    files_read = 0
    files_with_attributes = 0
    empty_files = read_log_file(LOG_EMPTY_FILES)
    processed_files = read_log_file(LOG_PROCESSED_FILES)
    scanned_files = read_log_file(LOG_SCANNED_FILES)

    # Determine files to scan based on mode
    if mode == 1:  # Full scan
        files_to_scan = None  # Scan all files
    elif mode == 2:  # Scan only new files
        files_to_scan = None  # We will dynamically filter out already scanned files
    elif mode == 3:  # Rescan empty files
        files_to_scan = empty_files
    elif mode == 4:  # Rescan files where attributes were already found
        files_to_scan = processed_files

    # Walk through all subdirectories and files
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_name_only = os.path.basename(filename)

            # Skip files based on mode
            if mode == 2 and file_name_only in scanned_files:  # Skip already scanned files in mode 2
                continue
            if files_to_scan and file_name_only not in files_to_scan:
                continue

            scanned_files.add(file_name_only)
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
                            elif "CustomApplicationRequirement" in entry["Properties"]:
                                for block in entry["Properties"]["CustomApplicationRequirement"]:
                                    if "GameplayModifierInfos" in block:
                                        process_attributes(
                                            block["GameplayModifierInfos"],
                                            file_name_only,
                                            attribute_to_files,
                                            module_extra_to_files,
                                            unique_attributes,
                                            attribute_files_map
                                        )
                                        found_attributes = True

                    # Update logs based on whether attributes were found
                    if found_attributes:
                        files_with_attributes += 1
                        processed_files.add(file_name_only)
                        # Ensure the file is removed from empty files if attributes are found
                        if file_name_only in empty_files:
                            empty_files.discard(file_name_only)
                    else:
                        # Only add to empty files if not already processed
                        if file_name_only not in processed_files:
                            empty_files.add(file_name_only)

                except json.JSONDecodeError:
                    error_message = f"Error reading {file_path}. Skipping."
                    print(error_message)
                    log_error_to_file(error_message)

    # Write updated logs
    write_to_log_file(LOG_EMPTY_FILES, empty_files, overwrite=True)  # Overwrite the log file
    write_to_log_file(LOG_PROCESSED_FILES, processed_files, overwrite=True)
    write_to_log_file(LOG_SCANNED_FILES, scanned_files, overwrite=True)

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
        if "GameplayModifierInfo" in modifier_info:
            attribute_info = modifier_info["GameplayModifierInfo"].get("Attribute", {})
        else:
            attribute_info = modifier_info.get("Attribute", {})

        if "AttributeName" in attribute_info:
            attribute_name = attribute_info["AttributeName"]
            module_extra_type = modifier_info.get("ModuleExtraType", "NoModule")

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
    os.makedirs(os.path.dirname(filename), exist_ok=True)
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
    with open(LOG_INFO, 'a', encoding='utf-8') as f:
        f.write(log_message)


if __name__ == "__main__":
    initialize_logs()

    print("Select scanning mode:")
    print("1. Full scan")
    print("2. Scan only new files")
    print("3. Rescan empty files")
    print("4. Rescan files with attributes found")
    mode = int(input("Enter mode (1/2/3/4): "))

    start_time = time.time()
    sorted_unique_attributes, attribute_files_map, attribute_to_files, module_extra_to_files, files_read, files_with_attributes = process_json_files(directory, mode)
    end_time = time.time()

    save_to_json('Exported/unique_attributes_sorted.json', sorted_unique_attributes)
    save_to_json('Exported/attribute_files_map1.json', attribute_files_map)
    save_to_json('Exported/attribute_to_module_mapping2.json', attribute_to_files)
    save_to_json('Exported/module_extra_to_files_mapping3.json', module_extra_to_files)

    log_summary(start_time, end_time, files_read, len(sorted_unique_attributes), files_with_attributes)
