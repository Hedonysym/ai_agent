import os
def get_file_content(working_directory, file_path):
    try:
        abs_path = os.path.abspath(working_directory)
        
    except:
        return f'Error: {working_directory} does not exist'
    joined_path = os.path.join(abs_path, file_path)
    if not joined_path.startswith(abs_path):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(joined_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    try:
        with open(joined_path, 'r') as file:
            content = file.read(10000)
    except:
        return f'Error: "{file_path}" not suceccsully opened'
    if len(content) == 10000:
        return f'{content}[...File "{file_path}" truncated at 10000 characters]'
    return content
    