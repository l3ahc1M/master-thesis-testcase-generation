
import os
import json
import requests
import shutil
from system_documentation.name_to_url import name_to_url

# Folder containing the test case JSON files, organized by subfolder (API name)
TESTCASE_FOLDER = "modified_input_testcases/API"
# Folder where successfully executed and verified test cases will be moved
VALIDATED_FOLDER = "validated_testcases/API"

def execute_test_cases():
    """
    Executes all API test cases found in the TESTCASE_FOLDER.
    For each subfolder (representing an API), it:
      - Looks up the base URL from the name_to_url mapping.
      - Iterates through all JSON files (test cases) in the subfolder.
      - Reads each test case, extracts HTTP method, endpoint, and optional body.
      - Sends the HTTP request to the constructed URL.
      - If the response status code is 200, 201, or 204, moves the test case file
        to the corresponding subfolder in VERIFIED_FOLDER.
      - Prints execution status and errors for each test case.
    """
    for subfolder in os.listdir(TESTCASE_FOLDER):
        subfolder_path = os.path.join(TESTCASE_FOLDER, subfolder)
        # Skip if not a directory (e.g., files in TESTCASE_FOLDER)
        if not os.path.isdir(subfolder_path):
            continue

        # Get the base URL for the current API/subfolder
        base_url = name_to_url.get(subfolder)
        if not base_url:
            print(f"Base URL not found for subfolder: {subfolder}")
            continue

        # Iterate through all JSON test case files in the subfolder
        for file_name in os.listdir(subfolder_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(subfolder_path, file_name)
                try:
                    # Load the test case JSON
                    with open(file_path, "r") as file:
                        test_case = json.load(file)
                    # Extract HTTP method, endpoint, and optional body
                    method = test_case["output"]["method"]
                    endpoint = test_case["output"]["endpoint"]
                    body = test_case["output"].get("body", None)
                    url = f"{base_url}{endpoint}"

                    # Send the HTTP request based on the method
                    if method.upper() == "GET":
                        response = requests.get(url, json=body)
                    elif method.upper() == "POST":
                        response = requests.post(url, json=body)
                    elif method.upper() == "PUT":
                        response = requests.put(url, json=body)
                    elif method.upper() == "DELETE":
                        response = requests.delete(url, json=body)
                    else:
                        print(f"Unsupported method: {method}")
                        continue

                    print(f"Executed {method} {url}: {response.status_code}")

                    # If the response is successful, move the test case to VERIFIED_FOLDER
                    if response.status_code in (200, 201, 204):
                        verified_subfolder = os.path.join(VALIDATED_FOLDER, subfolder)
                        os.makedirs(verified_subfolder, exist_ok=True)
                        shutil.move(file_path, os.path.join(verified_subfolder, file_name))

                except Exception as e:
                    print(f"Error with {file_path}: {e}")

def count_remaining_files():
    """
    Counts and prints the number of remaining (unverified) test case JSON files
    in each subfolder of TESTCASE_FOLDER.
    """
    for subfolder in os.listdir(TESTCASE_FOLDER):
        path = os.path.join(TESTCASE_FOLDER, subfolder)
        if os.path.isdir(path):
            count = len([f for f in os.listdir(path) if f.endswith(".json")])
            print(f"{subfolder}: {count} remaining files")
