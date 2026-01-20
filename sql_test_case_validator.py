import os
import json
import shutil
import sqlparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

TESTCASE_FOLDER = "modified_input_testcases/SQL"
VALIDATED_FOLDER = "validated_testcases/SQL"

def validate_sql_syntax(sql_code):
    """
    Validates SQL syntax using sqlparse.
    Returns True if the SQL can be parsed, False otherwise.
    """
    try:
        parsed = sqlparse.parse(sql_code)
        return bool(parsed)
    except Exception as e:
        logging.error(f"Exception during SQL parsing: {e}")
        return False

def validate_test_cases():
    """
    Validates all SQL test cases found in the TESTCASE_FOLDER.
    For each subfolder (representing a SQL category), it:
      - Iterates through all JSON files (test cases) in the subfolder.
      - Reads each test case, extracts the SQL statement.
      - Checks the SQL syntax using sqlparse.
      - If the syntax is valid, moves the test case file
        to the corresponding subfolder in VALIDATED_FOLDER.
      - Logs validation status and errors for each test case.
    """
    for subfolder in os.listdir(TESTCASE_FOLDER):
        subfolder_path = os.path.join(TESTCASE_FOLDER, subfolder)
        if not os.path.isdir(subfolder_path):
            continue

        for file_name in os.listdir(subfolder_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(subfolder_path, file_name)
                try:
                    with open(file_path, "r") as file:
                        test_case = json.load(file)
                    sql_code = test_case["output"]["sql"]

                    if validate_sql_syntax(sql_code):
                        logging.info(f"Valid SQL in {file_path}")
                        validated_subfolder = os.path.join(VALIDATED_FOLDER, subfolder)
                        os.makedirs(validated_subfolder, exist_ok=True)
                        shutil.move(file_path, os.path.join(validated_subfolder, file_name))
                    else:
                        logging.warning(f"Invalid SQL syntax in {file_path}")

                except Exception as e:
                    logging.error(f"Error processing {file_path}: {e}")

def count_remaining_files():
    """
    Counts and logs the number of remaining (unvalidated) test case JSON files
    in each subfolder of TESTCASE_FOLDER.
    """
    for subfolder in os.listdir(TESTCASE_FOLDER):
        path = os.path.join(TESTCASE_FOLDER, subfolder)
        if os.path.isdir(path):
            count = len([f for f in os.listdir(path) if f.endswith(".json")])
            logging.info(f"{subfolder}: {count} remaining files")



if __name__ == "__main__":
    validate_test_cases()
    count_remaining_files()