import os

def get_files_info(working_directory, directory=None):
    abs_path = os.path.abspath(working_directory)
    if directory is None:
        dir_path = abs_path
    else:
        dir_path = os.path.join(abs_path, directory)
    if not dir_path.startswith(abs_path):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(dir_path):
        return f'Error: "{directory}" is not a directory'
    try:
        dir_list = os.listdir(dir_path)
        final = []
        for item in dir_list:
            item_path = os.path.join(dir_path, item)
            final.append(f"- {item}: file_size={os.path.getsize(item_path)} bytes, is_dir={os.path.isdir(item_path)}\n")
        return ''.join(final)
    except:
        return f'Error: "{directory}" cannot be listed'
    
