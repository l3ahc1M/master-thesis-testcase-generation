import os
import json
import requests
import shutil
from system_documentation.name_to_url import name_to_url

# Base folder containing the test cases.
# Each subfolder under this directory should correspond to a system/component name.
TESTCASE_FOLDER = "updated_testcases/API"

# Folder where successfully executed (verified) test cases will be moved.
# The structure will mirror TESTCASE_FOLDER.
VERIFIED_FOLDER = "execution_verified_testcases/API"

def execute_test_cases():
    """
    Executes API test cases stored as JSON files in subfolders of TESTCASE_FOLDER.
    For each test case:
      - Reads the test case JSON file.
      - Extracts HTTP method, endpoint, and optional body from the test case.
      - Constructs the full API URL using a mapping from subfolder name to base URL.
      - Executes the API call using the requests library.
      - Prints the response status code.
      - If the response status code is 200, moves the test case file to the corresponding subfolder in VERIFIED_FOLDER.
      - Handles invalid JSON, missing base URLs, unsupported HTTP methods, and request exceptions gracefully.
    """
    for subfolder in os.listdir(TESTCASE_FOLDER):
        subfolder_path = os.path.join(TESTCASE_FOLDER, subfolder)
        
        # Skip if not a directory (e.g., skip files in TESTCASE_FOLDER)
        if not os.path.isdir(subfolder_path):
            continue
        
        # Get the base URL for the current subfolder (system/component)
        base_url = name_to_url.get(subfolder)
        if not base_url:
            print(f"Base URL not found for subfolder: {subfolder}")
            continue
        
        # Process each JSON file in the subfolder
        for file_name in os.listdir(subfolder_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(subfolder_path, file_name)
                
                # Load the test case JSON file
                with open(file_path, "r") as file:
                    try:
                        test_case = json.load(file)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON in file: {file_path}")
                        continue

                # Extract the API call details from the test case
                # The expected structure is:
                # {
                #   "output": {
                #     "method": "GET" | "POST" | "PUT" | "DELETE",
                #     "endpoint": "/api/endpoint",
                #     "body": {...} (optional)
                #   }
                # }
                method = test_case["output"]["method"]
                endpoint = test_case["output"]["endpoint"]
                body = test_case["output"].get("body", None)
                
                # Construct the full URL for the API call
                url = f"{base_url}{endpoint}"
                
                # Execute the API call using the appropriate HTTP method
                try:
                    if method.upper() == "GET":
                        # For GET requests, the body is sent as JSON (if present)
                        response = requests.get(url, json=body)
                    elif method.upper() == "POST":
                        response = requests.post(url, json=body)
                    elif method.upper() == "PUT":
                        response = requests.put(url, json=body)
                    elif method.upper() == "DELETE":
                        response = requests.delete(url, json=body)
                    else:
                        print(f"Unsupported HTTP method: {method} in file: {file_path}")
                        continue
                    
                    # Print the executed request and response status code
                    print(f"Executed {method} {url}")
                    print(f"Response: {response.status_code}")
                    
                    # If the response is successful (HTTP 200), move the file to the verified folder
                    if response.status_code in (200, 201, 204):
                        verified_subfolder = os.path.join(VERIFIED_FOLDER, subfolder)
                        os.makedirs(verified_subfolder, exist_ok=True)
                        shutil.move(file_path, os.path.join(verified_subfolder, file_name))
                        print(f"Moved file to {verified_subfolder}")
                
                except requests.RequestException as e:
                    # Handle network errors, timeouts, etc.
                    print(f"Error executing API call for file: {file_path}")
                    print(f"Error: {e}")

def count_remaining_files():
    """
    Counts and prints the number of remaining JSON files per subfolder in TESTCASE_FOLDER.
    """
    for subfolder in os.listdir(TESTCASE_FOLDER):
        subfolder_path = os.path.join(TESTCASE_FOLDER, subfolder)
        if not os.path.isdir(subfolder_path):
            continue
        json_files = [f for f in os.listdir(subfolder_path) if f.endswith(".json")]
        print(f"{subfolder}: {len(json_files)} remaining files")

if __name__ == "__main__":
    execute_test_cases()
    count_remaining_files()