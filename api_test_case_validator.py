import os
import json
import requests
import shutil
from system_documentation.name_to_url import name_to_url

TESTCASE_FOLDER = "modified_input_testcases/API"
VALIDATED_FOLDER = "validated_testcases/API"

def execute_test_cases():
    for subfolder in os.listdir(TESTCASE_FOLDER):
        subfolder_path = os.path.join(TESTCASE_FOLDER, subfolder)
        if not os.path.isdir(subfolder_path):
            continue

        base_url = name_to_url.get(subfolder)
        if not base_url:
            print(f"Base URL not found for subfolder: {subfolder}")
            continue

        for file_name in os.listdir(subfolder_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(subfolder_path, file_name)
                try:
                    with open(file_path, "r") as file:
                        test_case = json.load(file)
                    method = test_case["output"]["method"]
                    endpoint = test_case["output"]["endpoint"]
                    body = test_case["output"].get("body", None)
                    url = f"{base_url}{endpoint}"

                    if method.upper() == "GET":
                        response = requests.get(url, json=body)
                    elif method.upper() == "POST":
                        response = requests.post(url, json=body)
                    elif method.upper() == "PUT":
                        response = requests.put(url, json=body)
                    elif method.upper() == "DELETE":
                        response = requests.delete(url, json=body)
                    elif method.upper() == "PATCH":
                        response = requests.patch(url, json=body)
                    else:
                        print(f"Unsupported method: {method}")
                        continue

                    print(f"Executed {method} {url}: {response.status_code}")

                    if response.status_code in (200, 201, 204):
                        # Remove error log if present
                        if "error_log" in test_case:
                            del test_case["error_log"]
                            with open(file_path, "w") as file:
                                json.dump(test_case, file, indent=2)
                        verified_subfolder = os.path.join(VALIDATED_FOLDER, subfolder)
                        os.makedirs(verified_subfolder, exist_ok=True)
                        shutil.move(file_path, os.path.join(verified_subfolder, file_name))
                    else:
                        # Log error in the test case file
                        try:
                            response_json = response.json()
                            formatted_response = json.dumps(response_json, indent=2, ensure_ascii=False)
                        except Exception:
                            formatted_response = response.text
                        test_case["error_log"] = {
                            "status_code": response.status_code,
                            "response_text": formatted_response
                        }
                        with open(file_path, "w") as file:
                            json.dump(test_case, file, indent=2)

                except Exception as e:
                    print(f"Error with {file_path}: {e}")
                    # Log exception in the test case file
                    try:
                        with open(file_path, "r") as file:
                            test_case = json.load(file)
                        test_case["error_log"] = {
                            "exception": str(e)
                        }
                        with open(file_path, "w") as file:
                            json.dump(test_case, file, indent=2)
                    except Exception as inner_e:
                        print(f"Failed to log error in {file_path}: {inner_e}")

def count_remaining_files():
    for subfolder in os.listdir(TESTCASE_FOLDER):
        path = os.path.join(TESTCASE_FOLDER, subfolder)
        if os.path.isdir(path):
            count = len([f for f in os.listdir(path) if f.endswith(".json")])
            print(f"{subfolder}: {count} remaining files")
