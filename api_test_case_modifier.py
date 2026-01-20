# api_test_case_modifier.py
import os
import json
from llm_connector import OpenAIConnector

# Define the base path where the raw test cases are stored
base_path = "raw_testcases/API"
# Define the path where the updated (humanized) test cases will be saved
updated_base_path = "modified_input_testcases/API"

def humanize_testcases():
    """
    Iterates through all JSON test case files in the base_path directory structure.
    For each file, it rewrites the 'input' field of the test case to a more
    natural, human-friendly expression using an LLM. The modified test cases
    are saved in a corresponding mirrored structure under updated_base_path.

    The transformation preserves critical data integrity (like IDs or UUIDs)
    and aims for better readability and natural phrasing of test case prompts.
    """
    connector = OpenAIConnector()  # Initialize LLM connector
    for subfolder in os.listdir(base_path):
        subfolder_path = os.path.join(base_path, subfolder)
        if os.path.isdir(subfolder_path):
            for file_name in os.listdir(subfolder_path):
                if file_name.endswith(".json"):
                    file_path = os.path.join(subfolder_path, file_name)
                    try:
                        # Load the raw test case JSON data
                        with open(file_path, "r", encoding="utf-8") as file:
                            data = json.load(file)

                        # Format the input for the LLM
                        user_prompt = json.dumps(data, ensure_ascii=False)

                        # Instruction for the LLM to humanize the input text
                        system_prompt = """
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

                        # Send the prompt to the LLM and receive the rewritten input
                        rewritten_input = connector.query_without_file(system_prompt, user_prompt)

                        # Replace the original 'input' field with the humanized one
                        data["input"] = rewritten_input

                        # Prepare the destination folder and file path
                        updated_subfolder_path = os.path.join(updated_base_path, subfolder)
                        os.makedirs(updated_subfolder_path, exist_ok=True)
                        updated_file_path = os.path.join(updated_subfolder_path, file_name)

                        # Write the updated test case JSON
                        with open(updated_file_path, "w", encoding="utf-8") as updated_file:
                            json.dump(data, updated_file, indent=4, ensure_ascii=False)

                    except Exception as e:
                        # Handle unexpected exceptions and log the error
                        print(f"Error processing file {file_path}: {e}")

def compare_json_files(file1, file2):
    """
    Compares two JSON files by loading their content and ignoring the 'input' field.

    Args:
        file1 (str): Path to the first JSON file.
        file2 (str): Path to the second JSON file.

    Returns:
        bool: True if the files match in all fields except 'input', False otherwise.
    """
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    # Remove the 'input' field from both dictionaries
    data1.pop("input", None)
    data2.pop("input", None)

    # Compare remaining fields
    return data1 == data2

def evaluate_folders(folder1=base_path, folder2=updated_base_path):
    """
    Compares all JSON files in folder1 and folder2 to verify whether only the 'input'
    field has changed. Reports missing files or structural differences.

    Args:
        folder1 (str): Path to the original test cases directory.
        folder2 (str): Path to the updated (humanized) test cases directory.
    """
    for subdir, _, files in os.walk(folder1):
        # Compute relative and corresponding path in second folder
        rel_path = os.path.relpath(subdir, folder1)
        corresponding_subdir = os.path.join(folder2, rel_path)

        for file in files:
            if file.endswith('.json'):
                file1 = os.path.join(subdir, file)
                file2 = os.path.join(corresponding_subdir, file)

                # Report missing updated test case
                if not os.path.exists(file2):
                    print(f"File missing in second folder: {file2}")
                # Report structural differences beyond the 'input' field
                elif not compare_json_files(file1, file2):
                    print(f"Files differ beyond 'input': {file1} vs {file2}")
