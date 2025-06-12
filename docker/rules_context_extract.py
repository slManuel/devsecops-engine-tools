import sys
import csv

FILE_PATH = '/tmp/docs/rules.csv'
RULE_ID = sys.argv[1]

def proccess(file_path, rule_id):
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            content = list(reader)
            for item in content:
                if len(item) > 5 and item[0] == rule_id:
                    file_path_from_csv = f'/tmp/{item[5]}'
                    try:
                        with open(file_path_from_csv, 'r', encoding='utf-8') as file:
                            file_content = file.read()
                            print(file_content)
                    except FileNotFoundError:
                        print(f"File not found: {file_path_from_csv}")
                    except Exception as e:
                        print(f"Error reading file {file_path_from_csv}: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

proccess(file_path=FILE_PATH, rule_id=RULE_ID)