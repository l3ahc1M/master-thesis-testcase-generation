import os
import json
from collections import Counter, defaultdict

base_dir = 'system_documentation'
endpoint_counts = defaultdict(Counter)
total_counts = Counter()

for subfolder in os.listdir(base_dir):
    subfolder_path = os.path.join(base_dir, subfolder)
    if os.path.isdir(subfolder_path):
        for filename in os.listdir(subfolder_path):
            if filename.startswith('API_') and filename.endswith('.json'):
                file_path = os.path.join(subfolder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        spec = json.load(f)
                        paths = spec.get('paths', {})
                        for path, methods in paths.items():
                            for method in methods:
                                method_lower = method.lower()
                                endpoint_counts[filename][method_lower] += 1
                                total_counts[method_lower] += 1
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

# Print per specification
for spec, counts in endpoint_counts.items():
    print(f"{spec}:")
    for method, count in counts.items():
        print(f"  {method.upper()}: {count}")

# Print total counts
print("\nTotal endpoints per type:")
for method, count in total_counts.items():
    print(f"{method.upper()}: {count}")