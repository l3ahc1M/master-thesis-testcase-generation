# sql_test_case_modifier.py
import os
import json
import logging
from llm_connector import OpenAIConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

base_path = "raw_testcases/SQL"
updated_base_path = "modified_input_testcases/SQL"

def humanize_testcases():
    """
    Iterates through all JSON test case files in the base_path directory structure.
    For each file, it rewrites the 'input' field of the test case to a more
    natural, human-friendly expression using an LLM. The modified test cases
    are saved in a corresponding mirrored structure under updated_base_path.
    """
    connector = OpenAIConnector()
    for subfolder in os.listdir(base_path):
        subfolder_path = os.path.join(base_path, subfolder)
        if os.path.isdir(subfolder_path):
            for file_name in os.listdir(subfolder_path):
                if file_name.endswith(".json"):
                    file_path = os.path.join(subfolder_path, file_name)
                    try:
                        logging.info(f"Processing file: {file_path}")
                        with open(file_path, "r", encoding="utf-8") as file:
                            data = json.load(file)

                        user_prompt = json.dumps(data, ensure_ascii=False)
                        system_prompt = """
                            You will receive json objects containing SQL test cases. 
                            Each test case contains:
                            1. difficulty: describing the difficulty of the test case
                            2. input: the input of the test case (usually a description or requirement)
                            3. output: the expected output of the test case - an SQL query
                            Rewrite the input of the testcase to a more humanly written way. This includes:
                            - be colloquial and natural
                            - clarify abbreviations, table names, or column names if possible, but do not change any identifiers or values that are referenced in the SQL output
                            - make dates, numbers, and other values more human-readable where possible
                            - rephrase technical requirements into natural language, but keep them consistent with the SQL output
                            Never change any ID/UUID or any value that must match the SQL output.
                            Only return the value of the "input" of the json object. Respond only with the plain sentence, without quotation marks, formatting, or any extra characters at the beginning or end.
                        """

                        rewritten_input = connector.query_without_file(system_prompt, user_prompt)
                        data["input"] = rewritten_input

                        updated_subfolder_path = os.path.join(updated_base_path, subfolder)
                        os.makedirs(updated_subfolder_path, exist_ok=True)
                        updated_file_path = os.path.join(updated_subfolder_path, file_name)

                        with open(updated_file_path, "w", encoding="utf-8") as updated_file:
                            json.dump(data, updated_file, indent=4, ensure_ascii=False)

                        logging.info(f"Updated file saved: {updated_file_path}")

                    except Exception as e:
                        logging.error(f"Error processing file {file_path}: {e}", exc_info=True)

def compare_json_files(file1, file2):
    """
    Compares two JSON files by loading their content and ignoring the 'input' field.
    """
    try:
        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)
        data1.pop("input", None)
        data2.pop("input", None)
        return data1 == data2
    except Exception as e:
        logging.error(f"Error comparing files {file1} and {file2}: {e}", exc_info=True)
        return False

def evaluate_folders(folder1=base_path, folder2=updated_base_path):
    """
    Compares all JSON files in folder1 and folder2 to verify whether only the 'input'
    field has changed. Reports missing files or structural differences.
    """
    for subdir, _, files in os.walk(folder1):
        rel_path = os.path.relpath(subdir, folder1)
        corresponding_subdir = os.path.join(folder2, rel_path)

        for file in files:
            if file.endswith('.json'):
                file1 = os.path.join(subdir, file)
                file2 = os.path.join(corresponding_subdir, file)

                if not os.path.exists(file2):
                    logging.warning(f"File missing in second folder: {file2}")
                elif not compare_json_files(file1, file2):
                    logging.warning(f"Files differ beyond 'input': {file1} vs {file2}")

if __name__ == "__main__":
    humanize_testcases()
