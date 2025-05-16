import os
import json
import re
import time
import logging
from llm_connector import OpenAIConnector

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
# Set up logging to display informational messages with timestamps and severity.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# Number of test cases to generate per difficulty level.
test_cases_per_difficulty = 1

# System prompt for the LLM, describing the test case generation task and output format.
system_prompt = """
You are a test case generator. You will be provided with:
- A JSON file representing database structure.
- A JSON file representing API documentation (as attachment).
- A semantic description of the business entity in plain text.
- Previously generated test cases.

Based on these, generate multiple test cases simulating customer requests for the specified API endpoint.
Each test case must include:
1. A natural language user input.
2. The corresponding API call (method, endpoint, body if applicable).
3. The difficulty level: Easy, Medium, Hard, Very Hard.

Ensure high variance between the test cases and any previously generated ones. Avoid repetition and vary structure, intent, and data.

Return a JSON array of objects, where each object follows this format:
{
    "difficulty": "Easy|Medium|Hard|Very Hard",
    "input": "<natural language prompt>",
    "output": {
        "method": "GET|POST|PUT|DELETE",
        "endpoint": "<API endpoint>",
        "body": { ...optional JSON payload... }
    }
}
Always respond only with a valid JSON array.
"""

# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------

def extract_json_array(text):
        """
        Extracts a JSON array from a string. If the string is not a valid JSON array,
        attempts to find and parse the first JSON array within the string using regex.

        Args:
                text (str): The input string potentially containing a JSON array.

        Returns:
                list: The parsed JSON array.

        Raises:
                ValueError: If no valid JSON array can be extracted.
        """
        try:
                return json.loads(text)
        except json.JSONDecodeError:
                match = re.search(r'\[.*\]', text, re.DOTALL)
                if match:
                        try:
                                return json.loads(match.group())
                        except json.JSONDecodeError:
                                pass
        raise ValueError("No valid JSON array could be extracted.")

def get_previous_test_cases(output_dir):
        """
        Aggregates all previously generated test cases from JSON files in a directory.

        Args:
                output_dir (str): Path to the directory containing previous test case files.

        Returns:
                list: A list of previously generated test cases.
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

# -----------------------------------------------------------------------------
# Main Test Case Generation Function
# -----------------------------------------------------------------------------

def generate_test_cases():
        """
        Main function to generate API test cases using an LLM connector.
        For each API endpoint in the documentation, generates a set of test cases
        distributed across difficulty levels, using the database structure, semantic
        description, and previously generated test cases as context.

        The generated test cases are saved as individual JSON files in the output directory.
        """
        connector = OpenAIConnector()
        root_input_dir = "system_documentation"
        root_output_dir = os.path.join("raw_testcases", "API")
        difficulties = ["Easy", "Medium", "Hard", "Very Hard"]

        # Iterate over each subdirectory (representing a business entity or API group)
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

                # Ensure all required files are present
                if db_file and api_file and txt_file:
                        with open(os.path.join(base_dir, db_file), 'r') as dbf, \
                                 open(os.path.join(base_dir, api_file), 'r') as apif, \
                                 open(os.path.join(base_dir, txt_file), 'r') as txtf:
                                db_content = dbf.read()
                                semantic_description = txtf.read()

                        try:
                                # Load API documentation and iterate over endpoints and methods
                                api_json = json.load(open(os.path.join(base_dir, api_file)))
                                paths = api_json.get("paths", {})
                                for path, methods in paths.items():
                                        for method in methods:
                                                # Prepare a safe filename component for the endpoint
                                                endpoint_path = path.replace("/", "_").strip("_")

                                                # Gather all previously generated test cases for this output directory
                                                previous_cases = get_previous_test_cases(output_dir)
                                                previous_cases_json = json.dumps(previous_cases, indent=2)
                                                total_test_cases = test_cases_per_difficulty * len(difficulties)

                                                # Compose the user prompt for the LLM
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

                                                        # Save each generated test case as a separate JSON file
                                                        count = {level: 0 for level in difficulties}
                                                        for parsed in parsed_list:
                                                                diff = parsed.get("difficulty", "Unknown")
                                                                idx = count.get(diff, 0) + 1
                                                                count[diff] = idx

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

# Run the test case generation process when the script is executed.
generate_test_cases()
