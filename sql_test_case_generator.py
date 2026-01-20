import os
import json
import re
import time
import logging
from llm_connector import OpenAIConnector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

system_prompt = """
You are a test case generator. You will be provided with:
- A JSON file representing database structure.
- A semantic description of the business entity in plain text.
- Previously generated test cases.

If columns have the same name in different tables, they are considered the same column and can therefore be used to join these tables..

Based on these, generate multiple test cases simulating a bank clerk handling customer requests via a chat interface with an AI agent.
Each test case must include:
1. A natural language user input based on a customer request - needs to contain all information required for the SQL query.
2. The corresponding SQL SELECT query to retrieve the requested data.
3. The difficulty level: Easy, Medium, Hard, Extra Hard
3.1 example for Easy query: SELECT Count(*) FROM cars_data WHERE cylinders > 4;
3.2 example for Medium query: SELECT T2.name, COUNT(*) FROM concert AS T1 JOIN stadium AS T2 ON T1.stadium_id = T2.stadium_id GROUP BY T1.stadium_id;
3.3 example for Hard query: SELECT T1.country_name FROM countries AS T1 JOIN continents AS T2 ON T1.continent = T2.cont_id JOIN car_makers AS T3 ON T1.country_id = T3.country WHERE T2.continent = 'Europe' GROUP BY T1.country_name HAVING COUNT(*) > 3;
3.4 example for Extra Hard query: SELECT AVG(life_expectancy) FROM country WHERE name NOT IN (SELECT T1.name FROM country AS T1 JOIN country_language AS T2 ON T1.code = T2.country_code WHERE T2.language = "English" AND T2.is_official = "T") 

It is of the utmost importance that someone else can generate the same output using ONLY the provided documents and the input.

Ensure high variance between the test cases and any previously generated ones. Avoid repetition and vary structure, intent, and data.

Return a JSON array of objects, where each object follows this format:
{
    "difficulty": "Easy|Medium|Hard|Extra Hard",
    "input": "<natural language prompt>",
    "output": {
        "sql": "<SQL SELECT query>"
    }
}
Before providing the output, ensure that: you would be able to generate the whole output again using only the provided documents and the input. If not, regenerate your answer.
Always respond only with a valid JSON array.
"""

def extract_json_array(text):
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
    Generates SQL test cases for each business domain based on database structure and semantic descriptions.

    This function iterates through subdirectories in the specified input directory, each representing a business domain.
    For each domain, it loads the corresponding database structure and semantic description, and uses an AI connector
    to generate a specified number of test cases distributed evenly across predefined difficulty levels.
    The generated test cases are saved as JSON files in the appropriate output directory.

    Steps:
        1. Loads the combined database documentation.
        2. Iterates through each business domain subdirectory (excluding the combined_db.json file).
        3. For each domain:
            - Loads the domain-specific database structure and semantic description.
            - Retrieves previously generated test cases for the domain.
            - Constructs a prompt for the AI model including all relevant information.
            - Queries the AI model to generate new test cases.
            - Parses and saves each generated test case as a JSON file, organized by difficulty and timestamp.
        4. Handles and logs any errors encountered during processing.

    Dependencies:
        - Requires the OpenAIConnector class for querying the AI model.
        - Assumes the existence of helper functions: get_previous_test_cases and extract_json_array.
        - Uses the logging module for error and info logging.

    Raises:
        Logs exceptions encountered during file I/O, AI querying, or JSON parsing.

    Note:
        The number of test cases per difficulty and the system prompt must be defined elsewhere in the code.
    """
    connector = OpenAIConnector()
    root_input_dir = "system_documentation"
    root_output_dir = os.path.join("raw_testcases", "SQL")
    difficulties = ["Easy", "Medium", "Hard", "Extra Hard"]

    # Load combined DB documentation once
    combined_db_path = os.path.join(root_input_dir, "combined_db.json")
    with open(combined_db_path, 'r') as cdbf:
        combined_db_content = cdbf.read()

    for subdir in os.listdir(root_input_dir):
        base_dir = os.path.join(root_input_dir, subdir)
        if not os.path.isdir(base_dir) or subdir == "combined_db.json":
            continue

        output_dir = os.path.join(root_output_dir, subdir)
        os.makedirs(output_dir, exist_ok=True)

        filenames = os.listdir(base_dir)
        db_file = next((f for f in filenames if f.startswith("DB_") and f.endswith(".json")), None)
        txt_file = next((f for f in filenames if f.endswith(".txt")), None)

        if db_file and txt_file:
            with open(os.path.join(base_dir, db_file), 'r') as dbf, \
                 open(os.path.join(base_dir, txt_file), 'r') as txtf:
                db_content = dbf.read()
                semantic_description = txtf.read()

            try:
                previous_cases = get_previous_test_cases(output_dir)
                previous_cases_json = json.dumps(previous_cases, indent=2)
                total_test_cases = test_cases_per_difficulty * len(difficulties)

                user_prompt = f"""
                Combined Database Structure (all business objects):
                {combined_db_content}

                Database Structure for this business domain:
                {db_content}

                Semantic Description for this business domain:
                {semantic_description}

                Previously Generated Test Cases:
                {previous_cases_json}

                Generate {total_test_cases} test cases distributed evenly across the following difficulty levels: {difficulties}.
                The test cases should focus on the business domain '{subdir}', but need to involve related business objects from the combined database.
                """

                try:
                    response = connector.query_with_file(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        file_path=os.path.join(base_dir, db_file),
                        model="gpt-4o-mini"
                    )
                    parsed_list = extract_json_array(response)

                    count = {level: 0 for level in difficulties}
                    for parsed in parsed_list:
                        diff = parsed.get("difficulty", "Unknown")
                        idx = count.get(diff, 0) + 1
                        count[diff] = idx

                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"{subdir}_{diff}_{idx}_{timestamp}.json"
                        output_path = os.path.join(output_dir, filename)
                        with open(output_path, "w") as outfile:
                            json.dump(parsed, outfile, indent=2)
                        logging.info(f"Generated: {output_path}")

                except Exception as e:
                    logging.error(f"Error processing {subdir}: {e}")
            except Exception as e:
                logging.error(f"Failed to process {subdir}: {e}")

