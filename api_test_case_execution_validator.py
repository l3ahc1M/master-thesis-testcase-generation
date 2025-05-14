import os
import json
import requests
import shutil
from system_documentation.name_to_url import name_to_url

# Base folder containing the test cases
TESTCASE_FOLDER = "updated_testcases/API"
VERIFIED_FOLDER = "execution_verified/API"

def execute_test_cases():
    for subfolder in os.listdir(TESTCASE_FOLDER):
        subfolder_path = os.path.join(TESTCASE_FOLDER, subfolder)
        
        # Skip if not a directory
        if not os.path.isdir(subfolder_path):
            continue
        
        # Get the base URL for the current subfolder
        base_url = name_to_url.get(subfolder)
        if not base_url:
            print(f"Base URL not found for subfolder: {subfolder}")
            continue
        
        # Process each JSON file in the subfolder
        for file_name in os.listdir(subfolder_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(subfolder_path, file_name)
                
                with open(file_path, "r") as file:
                    try:
                        test_case = json.load(file)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON in file: {file_path}")
                        continue
                # Extract the API call details
                method = test_case["output"]["method"]
                endpoint = test_case["output"]["endpoint"]
                body = test_case["output"].get("body", None)
                
                # Construct the full URL
                url = f"{base_url}{endpoint}"
                
                # Execute the API call
                try:
                    if method.upper() == "GET":
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
                    
                    # Print the response
                    print(f"Executed {method} {url}")
                    print(f"Response: {response.status_code}")
                    
                    # Move the file if the response status code is 200
                    if response.status_code == 200:
                        verified_subfolder = os.path.join(VERIFIED_FOLDER, subfolder)
                        os.makedirs(verified_subfolder, exist_ok=True)
                        shutil.move(file_path, os.path.join(verified_subfolder, file_name))
                        print(f"Moved file to {verified_subfolder}")
                
                except requests.RequestException as e:
                    print(f"Error executing API call for file: {file_path}")
                    print(f"Error: {e}")

if __name__ == "__main__":
    execute_test_cases()