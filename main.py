import time

# Import functions from the individual modules of the test case pipeline
from api_test_case_generator import generate_test_cases
from api_test_case_modifier import humanize_testcases, evaluate_folders
from api_test_case_execution_validator import execute_test_cases, count_remaining_files

def main():
    # Step 1: Generate initial API test cases from system and API documentation
    print("Step 1: Generating Test Cases")
    start = time.time()
    generate_test_cases()
    step1_time = time.time() - start
    print(f"Step 1 took {step1_time:.2f} seconds.")

    # Step 2: Humanize the test cases to improve readability for QA and stakeholders
    print("\nStep 2: Humanizing Test Cases")
    start = time.time()
    humanize_testcases()
    evaluate_folders()
    step2_time = time.time() - start
    print(f"Step 2 took {step2_time:.2f} seconds.")

    # Step 3: Execute the test cases against live API endpoints and validate responses
    print("\nStep 3: Executing and Validating Test Cases")
    start = time.time()
    execute_test_cases()
    count_remaining_files()
    step3_time = time.time() - start
    print(f"Step 3 took {step3_time:.2f} seconds.")

    total_time = step1_time + step2_time + step3_time
    print(f"Step 1 took {step1_time:.2f} seconds.")
    print(f"Step 2 took {step2_time:.2f} seconds.")
    print(f"Step 3 took {step3_time:.2f} seconds.")
    print(f"\nTotal execution time: {total_time:.2f} seconds.")

# Entry point for the script when run directly
if __name__ == "__main__":
    main()
