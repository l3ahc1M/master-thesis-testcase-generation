# api_test_case_generator.py

import os
import json
import re
import time
import logging
from llm_connector import OpenAIConnector

# Configure logging to display timestamps, log level, and messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# System prompt for the LLM, describing the requirements for test case generation
system_prompt = """
You are a test case generator. You will be provided with:
- A JSON file representing database structure.
- A JSON file representing API documentation (as attachment).
- A semantic description of the business entity in plain text.
- Previously generated test cases.

Based on these, generate multiple test cases simulating a bank clerk handling customer requests via a chat interface with an AI agent.
Each test case must include:
1. A natural language user input based on a customer request - needs to contain all information required for the API call.
2. The corresponding API call (method, endpoint, body if applicable).
3. The difficulty level: Easy, Medium, Hard, Extra Hard. 
3.1. Example of an Easy API call: "method": "GET", "endpoint": "/GetTransactionCount", "params": {"userId": "12345"}
3.2. Example of a Medium API call: "method": "POST","endpoint": "/GetSpendingByCategory", "body": {"accountId": "98765", "month": "2024-05"}
3.3. Example of a Hard API call: "method": "POST", "endpoint": "/GetHighValueCustomers", "body": {"transactionThreshold": 5, "currency": "EUR"}
3.4. Example of an Extra Hard API call: "method": "POST", "endpoint": "/CalculateAvgPurchase", "body": {"exclude": {"usedCoupon": true,"inLoyaltyProgram": true},"aggregation": "average","field": "purchaseAmount"}

Note that the examples above are illustrative and should not be used as actual test cases. You must stick to the provided API documentation and the semantic description to create realistic test cases.

It is of the utmost importance that someone else can generate the same output using ONLY the provided documents and the input.

You must always include all parameters required for the API call incl. the body in the "input".

Ensure high variance between the test cases and any previously generated ones. Avoid repetition and vary structure, intent, and data.

Return a JSON array of objects, where each object follows this format:
{
    "difficulty": "Easy|Medium|Hard|Very Hard",
    "input": "<natural language prompt>",
    "output": {
        "method": "POST|PUT|DELETE",
        "endpoint": "<API endpoint>",
        "body": { ...optional JSON payload... }
    }
}
Before providing the output, ensure that: you would be able to gernerate the whole output again using only the provided documents and the input. If not, regenerate your answer.
Always respond only with a valid JSON array.
"""  

def extract_json_array(text):
    """
    Attempts to extract and parse a JSON array from a string.
    Handles cases where the response may contain extra text or formatting.

    Args:
        text (str): The input string potentially containing a JSON array.

    Returns:
        list: The parsed JSON array.

    Raises:
        ValueError: If no valid JSON array could be extracted.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract the first JSON array found in the text
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    raise ValueError("No valid JSON array could be extracted.")

def get_previous_test_cases(output_dir):
    """
    Loads all previously generated test cases from a directory.

    Args:
        output_dir (str): Path to the directory containing test case JSON files.

    Returns:
        list: A list of previously generated test cases (as dicts).
    """
    test_cases = []
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(output_dir, file), 'r') as f:
                        test_case = json.load(f)
                        if isinstance(test_case, list):
                            test_cases.extend(test_case)
                        else:
                            test_cases.append(test_case)
                except Exception:
                    continue
    return test_cases

def generate_test_cases(test_cases_per_difficulty=1):
    """
    Main function to generate test cases for all API endpoints found in the documentation.
    For each endpoint and HTTP method, it:
      - Loads the database structure, API documentation, and semantic description.
      - Retrieves previously generated test cases for the endpoint.
      - Constructs a prompt and queries the LLM to generate new test cases.
      - Saves each generated test case as a separate JSON file, organized by endpoint and difficulty.
    """
    connector = OpenAIConnector()
    root_input_dir = "system_documentation"  # Directory containing input files for each API
    root_output_dir = os.path.join("raw_testcases", "API")  # Output directory for generated test cases
    difficulties = ["Easy", "Medium", "Hard", "Extra Hard"]

    # Iterate over each subdirectory (representing an API or business entity)
    for subdir in os.listdir(root_input_dir):
        base_dir = os.path.join(root_input_dir, subdir)
        if not os.path.isdir(base_dir):
            continue

        output_dir = os.path.join(root_output_dir, subdir)
        os.makedirs(output_dir, exist_ok=True)

        filenames = os.listdir(base_dir)
        # Identify the relevant files by naming convention
        db_file = next((f for f in filenames if f.startswith("DB_") and f.endswith(".json")), None)
        api_file = next((f for f in filenames if f.startswith("API_") and f.endswith(".json")), None)
        txt_file = next((f for f in filenames if f.endswith(".txt")), None)

        if db_file and api_file and txt_file:
            with open(os.path.join(base_dir, db_file), 'r') as dbf, \
                 open(os.path.join(base_dir, api_file), 'r') as apif, \
                 open(os.path.join(base_dir, txt_file), 'r') as txtf:
                db_content = dbf.read()
                semantic_description = txtf.read()

            try:
                # Load API documentation to extract endpoints and methods
                api_json = json.load(open(os.path.join(base_dir, api_file)))
                paths = api_json.get("paths", {})
                for path, methods in paths.items():
                    for method in methods:
                        # Skip non-HTTP method keys and GET requests (if desired)
                        if method.lower() in ["parameters", "get"]:
                            continue

                        # Prepare a unique identifier for the endpoint
                        endpoint_path = path.replace("/", "_").strip("_")
                        previous_cases = get_previous_test_cases(output_dir)
                        previous_cases_json = json.dumps(previous_cases, indent=2)
                        total_test_cases = test_cases_per_difficulty * len(difficulties)

                        # Construct the user prompt for the LLM
                        user_prompt = f"""
                        Database Structure:
                        {db_content}

                        Semantic Description:
                        {semantic_description}

                        Previously Generated Test Cases:
                        {previous_cases_json}

                        Focus Endpoint: {path} using {method.upper()}

                        Generate {total_test_cases} test cases distributed evenly across the following difficulty levels: {difficulties}.
                        """

                        try:
                            # Query the LLM to generate test cases
                            response = connector.query_with_file(
                                system_prompt=system_prompt,
                                user_prompt=user_prompt,
                                file_path=os.path.join(base_dir, api_file),
                                model="gpt-4o-mini"
                            )
                            parsed_list = extract_json_array(response)

                            # Track the number of test cases per difficulty
                            count = {level: 0 for level in difficulties}
                            for parsed in parsed_list:
                                diff = parsed.get("difficulty", "Unknown")
                                idx = count.get(diff, 0) + 1
                                count[diff] = idx

                                # Generate a timestamped filename for each test case
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                filename = f"{endpoint_path}_{method.upper()}_{diff}_{idx}_{timestamp}.json"
                                output_path = os.path.join(output_dir, filename)
                                with open(output_path, "w") as outfile:
                                    json.dump(parsed, outfile, indent=2)
                                logging.info(f"Generated: {output_path}")

                        except Exception as e:
                            logging.error(f"Error processing {subdir} - {path} ({method}): {e}")
            except Exception as e:
                logging.error(f"Failed to process {subdir}: {e}")
