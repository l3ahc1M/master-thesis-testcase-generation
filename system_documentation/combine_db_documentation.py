import os
import json

def combine_db_json_files(directory, output_file):
    combined_data = []

    # Walk through the directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith("DB_") and file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Extract and append the content of the "tables" key if it exists
                        if "tables" in data:
                            combined_data.extend(data["tables"])
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error reading {file_path}: {e}")

    # Write combined data to the output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=4)
        print(f"Combined JSON written to {output_file}")
    except IOError as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(directory, "combined_db.json")
    combine_db_json_files(directory, output_file)