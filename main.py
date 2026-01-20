import time
import os
import glob

# Import functions from the individual modules of the test case pipeline
from api_test_case_generator import generate_test_cases as generate_api_test_cases
from api_test_case_modifier import humanize_testcases as humanize_api_testcases, evaluate_folders as evaluate_api_folders
from api_test_case_validator import execute_test_cases as validate_api_test_cases, count_remaining_files as count_remaining_api_files

from sql_test_case_generator import generate_test_cases as generate_sql_test_cases
from sql_test_case_modifier import humanize_testcases as humanize_sql_testcase, evaluate_folders as evaluate_sql_folders        
from sql_test_case_validator import validate_test_cases as validate_sql_test_cases, count_remaining_files as count_sql_remaining_files


def main():

    # Define flags to control the execution of each step in the pipeline
    number_of_api_test_cases_per_difficulty = 1
    to_generate_api_test_cases = False
    to_modify_api_test_cases = False
    to_validate_api_test_cases = False

    number_of_sql_test_cases_per_difficulty = 4
    to_generate_sql_test_cases = True
    to_modify_sql_test_cases = True
    to_validate_sql_test_cases = True

    start = time.time()

    # Step 1: Generate initial API test cases from system and API documentation
    if to_generate_api_test_cases:
        print(f"API Step 1: Generating Test Cases // {time.time()}")
        generate_api_test_cases(number_of_api_test_cases_per_difficulty)

    # Step 2: Humanize the test cases to improve readability for QA and stakeholders
    if to_modify_api_test_cases:
        print(f"API Step 2: Humanizing Test Cases // {time.time()}")
        humanize_api_testcases()
        evaluate_api_folders()

    # Step 3: Execute the test cases against live API endpoints and validate responses
    if to_validate_api_test_cases:
        print(f"API Step 3: Executing and Validating Test Cases // {time.time()}")
        validate_api_test_cases()
        count_remaining_api_files()

    api_total_time = time.time() - start
    print(f"\nTotal execution time for API test cases: {api_total_time:.2f} seconds.")

    if to_generate_sql_test_cases:
        print(f"SQL Step 1: Generating Test Cases // {time.time()}")
        generate_sql_test_cases(number_of_sql_test_cases_per_difficulty)
    
    if to_modify_sql_test_cases:
        print(f"SQL Step 2: Humanizing Test Cases // {time.time()}")
        humanize_sql_testcase()
        evaluate_sql_folders()

    if to_validate_sql_test_cases:
        print(f"SQL Step 3: Executing and Validating Test Cases // {time.time()}")
        validate_sql_test_cases()
        count_sql_remaining_files()

    sql_total_time = time.time() - start
    print(f"\nTotal execution time for SQL test cases: {sql_total_time:.2f} seconds.")

def count_json_files_in_subfolders(parent_folder):
    total = 0
    for root, dirs, files in os.walk(parent_folder):
        json_files = glob.glob(os.path.join(root, "*.json"))
        total += len(json_files)
    return total



# Entry point for the script when run directly
if __name__ == "__main__":
    main()
    api_json_count = count_json_files_in_subfolders("validated_testcases/API")
    sql_json_count = count_json_files_in_subfolders("validated_testcases/SQL")

    print(f"Number of JSON files in validated_testcases/API: {api_json_count}")
    print(f"Number of JSON files in validated_testcases/SQL: {sql_json_count}")
