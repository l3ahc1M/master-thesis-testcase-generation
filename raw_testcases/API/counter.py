import os

def count_files_in_subfolders(folder_path):
    file_count = 0
    for root, _, files in os.walk(folder_path):
        file_count += len(files)
    return file_count

if __name__ == "__main__":
    folder_path = os.path.dirname(os.path.abspath(__file__))
    total_files = count_files_in_subfolders(folder_path)
    print(f"Total number of files in all subfolders: {total_files}")