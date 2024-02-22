import subprocess
import shutil
import re

def read_exempt_errors(file_path):
    try:
        with open(file_path, 'r') as file:
            exempt_errors = [error.strip() for error in file.readlines()]
        return exempt_errors
    except FileNotFoundError:
        print(f"Exempt errors file {file_path} not found.")
        return []

def run_script(script_path):
    try:
        output = subprocess.check_output(['python', script_path], stderr=subprocess.STDOUT, text=True)
        return None  
    except subprocess.CalledProcessError as e:
        return e.output  

def find_error_line(error_message):
    match = re.search(r'File "' + re.escape(script_path) + r'", line (\d+),', error_message)
    if match:
        return int(match.group(1))
    return None

def delete_line(file_path, line_number):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for i, line in enumerate(lines, 1):
            if i != line_number:
                file.write(line)

def main(script_path, replacement_script_path, exempt_errors_file_path):
    exempt_errors = read_exempt_errors(exempt_errors_file_path)
    
    while True:
        error_message = run_script(script_path)
        if not error_message:
            print("Script completed successfully.")
            break
        
        if any(exempt_error in error_message for exempt_error in exempt_errors):
            print("Exempt error No action needed.")
            break
        
        line_number = find_error_line(error_message)
        if line_number:
            delete_line(script_path, line_number)
            print(f"Error on line {line_number}. Attempting to delete line and restart.")
        else:
            print("Could not identify the error line. Replacing script.")
            shutil.copy(replacement_script_path, script_path)
            break

if __name__ == "__main__":
    script_path = '/home/parallels/Desktop/new_ai/main.py'
    replacement_script_path = '/home/parallels/Desktop/new_ai/main2.py'
    exempt_errors_file_path = '/home/parallels/Desktop/new_ai/exempt_errors.txt'
    
    main(script_path, replacement_script_path, exempt_errors_file_path)
