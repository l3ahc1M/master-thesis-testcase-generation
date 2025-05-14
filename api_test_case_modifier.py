import os
import json

from llm_connector import OpenAIConnector

# Original path to the folder containing test cases
base_path = "raw_testcases\API"
# Destination base path for updated test cases
updated_base_path = "updated_testcases\API"

def humanize_testcases():
    connector = OpenAIConnector()
    for subfolder in os.listdir(base_path):
        subfolder_path = os.path.join(base_path, subfolder)
        if os.path.isdir(subfolder_path):
            for file_name in os.listdir(subfolder_path):
                if file_name.endswith(".json"):
                    file_path = os.path.join(subfolder_path, file_name)
                    with open(file_path, "r", encoding="utf-8") as file:
                        try:
                            data = json.load(file)
                            input_text = json.dumps(data, ensure_ascii=False)

                            instruction = """
                            You will receive json objects containting test cases. 
                            Each test case contains
                            1. difficulty: describing the difficulty of the test case
                            2. input: the input of the test case
                            2. output: the expected output of the test case - an API call
                            Rewrite the input of the testcase to a more humanly written way. This includes:
                            - be colloquial
                            - modify other of the input to make it more humanly written. e.g. changing country codes to full country names, changing timestamps to a more human-readable format, etc.
                            - modify value names to be more humanly written. e.g. changing "user_id" to "the user with the id" or currency codes to "currency"
                            However, it is crucial to keep it consistent with the output. This includes that you must never change any ID/UUID. 
                            Only return the value of the "input" of the json object. Respond only with the plain sentence, without quotation marks, formatting, or any extra characters at the beginning or end.
                            """
                            rewritten_input = connector.query_without_file(instruction, input_text)
                            print(f"Rewritten input: {rewritten_input}")
                            # Update the input in the JSON
                            data["input"] = rewritten_input

                            # Prepare the output directory and file path
                            updated_subfolder_path = os.path.join(updated_base_path, subfolder)
                            os.makedirs(updated_subfolder_path, exist_ok=True)
                            updated_file_path = os.path.join(updated_subfolder_path, file_name)

                            # Save the updated JSON
                            with open(updated_file_path, "w", encoding="utf-8") as updated_file:
                                json.dump(data, updated_file, indent=4, ensure_ascii=False)

                        except json.JSONDecodeError:
                            print(f"Error decoding JSON in file: {file_path}")
                        except Exception as e:
                            print(f"Error processing file {file_path}: {e}")

# Function to compare two JSON files, ignoring the "input" field
def compare_json_files(file1, file2):
    # Open and load the JSON files
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    # Remove the "input" field from both JSON objects for comparison
    data1_without_input = {key: value for key, value in data1.items() if key != "input"}
    data2_without_input = {key: value for key, value in data2.items() if key != "input"}

    # Return whether the two JSON objects (excluding "input") are equal
    return data1_without_input == data2_without_input

# Function to evaluate and compare JSON files in two folder structures
def evaluate_folders(folder1, folder2):
    # Walk through all subdirectories and files in the first folder
    for subdir, _, files in os.walk(folder1):
        # Get the relative path of the current subdirectory
        relative_path = os.path.relpath(subdir, folder1)
        # Determine the corresponding subdirectory in the second folder
        corresponding_subdir = os.path.join(folder2, relative_path)

        # Iterate over all files in the current subdirectory
        for file in files:
            # Process only JSON files
            if file.endswith('.json'):
                # Construct full paths for the files in both folders
                file1 = os.path.join(subdir, file)
                file2 = os.path.join(corresponding_subdir, file)

                # Check if the corresponding file exists in the second folder
                if not os.path.exists(file2):
                    print(f"File missing in second folder: {file2}")
                    continue

                # Compare the JSON files and report differences
                if not compare_json_files(file1, file2):
                    print(f"Files differ beyond 'input': {file1} and {file2}")

if __name__ == "__main__":
    # Create updated test cases
    humanize_testcases()

    # Evaluate update test cases
    evaluate_folders(base_path, updated_base_path)
