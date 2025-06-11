import os

def write_file(working_directory, file_path, content):
    try:
        abs_path = os.path.abspath(working_directory)
    except:
        return f'Error: {working_directory} does not exist'
    joined_path = os.path.join(abs_path, file_path)
    if not joined_path.startswith(abs_path):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(joined_path):
        dir_path = os.path.dirname(joined_path)
        os.makedirs(dir_path, exist_ok=True)
    try:
        with open(joined_path, 'w') as file:
            file.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except:
        return f'Error: "{file_path}" not suceccsully opened'

