import json
import os

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_path = os.path.join(repo_root, "system_documentation", "combined_db.json")

def extract_tables_and_columns(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tables = data.get("tables", [])
    for table in tables:
        print(f"Table: {table.get('name')}")
        desc = table.get('description', '')
        print(f"  Description: {desc.splitlines()[0] if desc else ''}")
        print("  Columns:")
        for col in table.get("columns", []):
            col_desc = col.get('description', '')
            print(f"    - {col.get('name')}: {col_desc.splitlines()[0] if col_desc else ''} (Format: {col.get('format', 'N/A')})")
        print()

if __name__ == "__main__":
    extract_tables_and_columns(json_path)