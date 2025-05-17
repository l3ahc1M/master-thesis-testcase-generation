# Master Thesis Test Case Generation

This repository provides an automated framework for generating, humanizing, and validating API test cases for banking domain APIs using Large Language Models (LLMs). The framework simulates realistic bank clerk-customer interactions and produces structured test cases for various banking APIs.

## Features

- **Automated Test Case Generation:**  
  Generates diverse test cases for each API endpoint using database structure, API documentation, and semantic descriptions with LLMs.

- **Humanization of Test Cases:**  
  Transforms technical test case inputs into natural, human-friendly language while preserving data integrity.

- **Test Case Validation:**  
  Validates generated test cases for correctness and consistency.

- **Extensible Documentation:**  
  Provides scripts and data for extracting and documenting API and database structures.

## Repository Structure

```
.
├── api_test_case_generator.py             # Main script for generating test cases
├── api_test_case_modifier.py              # Script for humanizing test case inputs
├── api_test_case_execution_validator.py   # Script for validating test case execution
├── llm_connector.py                       # LLM connector abstraction
├── main.py                                # Entry point (if applicable)
├── raw_testcases/                         # Generated raw test cases (gitignored)
├── updated_testcases/                     # Humanized test cases (gitignored)
├── execution_verified_testcases/          # Verified test cases (gitignored)
├── system_documentation/                  # API/database docs and semantic descriptions
│   ├── <api_name>/
│   │   ├── DB_<api_name>.json             # Database structure for the API
│   │   ├── API_<api_name>.json            # OpenAPI/Swagger spec for the API
│   │   └── <api_name>.txt                 # Semantic description of the API
│   └── combined_db.json                   # Combined database structure
├── .env                                   # Environment variables (gitignored)
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key (or compatible LLM provider)
- Required Python packages (see `requirements.txt`)

### Installation

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd master-thesis-testcase-generation
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in your API keys and settings.

### Usage

#### 1. Generate Test Cases

Run the test case generator to create raw test cases for all APIs:

```sh
python api_test_case_generator.py
```

Test cases are saved in `raw_testcases/API/<api_name>/`.

#### 2. Humanize Test Cases

Convert technical test case inputs to human-friendly language:

```sh
python api_test_case_modifier.py
```

Humanized test cases are saved in `updated_testcases/`.

#### 3. Validate Test Cases

Validate the execution of test cases (if implemented):

```sh
python api_test_case_execution_validator.py
```

#### 4. Extend Documentation

To extract or update API/database documentation, use:

```sh
python system_documentation/create_db_documentation.py
```

## Customization

- Add new APIs by placing their documentation and database structure in `system_documentation/<api_name>/`.
- Adjust the number of test cases per difficulty in [`api_test_case_generator.py`](api_test_case_generator.py).

## License

This project is for academic and research purposes. See [LICENSE](LICENSE) for details.

## Acknowledgements

- OpenAI for LLM APIs
- [Your University/Advisor, if applicable]

---

For questions or contributions, please open an issue or pull request.