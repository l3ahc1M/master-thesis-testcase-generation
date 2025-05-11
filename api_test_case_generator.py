import os
import json
import re
import time
from llm_connector import OpenAIConnector

system_prompt = """
You are a test case generator. You will be provided with:
- A JSON file representing database structure.
- A JSON file representing API documentation.
- A semantic description of the business entity in plain text.
- Previously generated test cases.

Based on these, generate a new test case simulating a customer request.
Make sure the test case includes:
1. A natural language user input.
2. The corresponding API call (method, endpoint, body if applicable).
3. The difficulty level: Easy, Medium, Hard, Very Hard.

Ensure high variance with the provided previous test cases. Avoid repetition and try to vary structure, intent, and data.

Respond in this JSON format:
{
  "difficulty": "Easy|Medium|Hard|Very Hard",
  "input": "<natural language prompt>",
  "output": {
    "method": "GET|POST|PUT|DELETE",
    "endpoint": "<API endpoint>",
    "body": { ...optional JSON payload... }
  }
}
Always provide only a valid json response starting and ending with { and }.
"""

def extract_json_block(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    raise ValueError("No valid JSON object could be extracted.")

def get_previous_test_cases(output_dir):
    test_cases = []
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(output_dir, file), 'r') as f:
                        test_case = json.load(f)
                        test_cases.append(test_case)
                except Exception:
                    continue
    return test_cases

def generate_test_cases_for_all_subfolders():
    connector = OpenAIConnector()
    root_input_dir = "system_documentation"
    root_output_dir = os.path.join("raw_testcases", "API")

    difficulties = ["Easy", "Medium", "Hard", "Very Hard"]

    for subdir in os.listdir(root_input_dir):
        base_dir = os.path.join(root_input_dir, subdir)
        if not os.path.isdir(base_dir):
            continue

        output_dir = os.path.join(root_output_dir, subdir)
        os.makedirs(output_dir, exist_ok=True)

        filenames = os.listdir(base_dir)
        db_file = next((f for f in filenames if f.startswith("DB_") and f.endswith(".json")), None)
        api_file = next((f for f in filenames if f.startswith("API_") and f.endswith(".json")), None)
        txt_file = next((f for f in filenames if f.endswith(".txt")), None)

        if db_file and api_file and txt_file:
            with open(os.path.join(base_dir, db_file), 'r') as dbf, \
                 open(os.path.join(base_dir, api_file), 'r') as apif, \
                 open(os.path.join(base_dir, txt_file), 'r') as txtf:
                db_content = dbf.read()
                api_content = apif.read()
                semantic_description = txtf.read()

            try:
                api_json = json.loads(api_content)
                paths = api_json.get("paths", {})
                for path, methods in paths.items():
                    for method in methods:
                        endpoint_path = path.replace("/", "_").strip("_")
                        for difficulty in difficulties:
                            for i in range(2):  # Generate 2 test cases per difficulty
                                previous_cases = get_previous_test_cases(output_dir)
                                previous_cases_json = json.dumps(previous_cases, indent=2)

                                user_prompt = f"""
Database Structure:
{db_content}

API Documentation:
{api_content}

Semantic Description:
{semantic_description}

Previously Generated Test Cases:
{previous_cases_json}

Focus Endpoint: {path} using {method.upper()}

Generate one test case of difficulty: {difficulty}.
"""

                                try:
                                    response = connector.query(
                                        system_prompt=system_prompt,
                                        user_prompt=user_prompt,
                                        model="gpt-4o",
                                        max_tokens=700,
                                        temperature=0
                                    )
                                    parsed = extract_json_block(response)

                                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                                    filename = f"{endpoint_path}_{method.upper()}_{difficulty}_{i+1}_{timestamp}.json"
                                    output_path = os.path.join(output_dir, filename)

                                    with open(output_path, "w") as outfile:
                                        json.dump(parsed, outfile, indent=2)
                                    print(f"Generated: {output_path}")

                                except Exception as e:
                                    print(f"Error processing {subdir} - {path} ({method}) [{difficulty} #{i+1}]: {e}")
            except Exception as e:
                print(f"Failed to process {subdir}: {e}")

# Run
generate_test_cases_for_all_subfolders()
