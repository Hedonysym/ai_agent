import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python import run_python_file
from functions.write_file import write_file

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.

to use the working directory directly, the directory argument should be '.'
"""
model_name = 'gemini-2.0-flash-001'

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the first 10,000 characters of a file's contents, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to be read, relative to the working directory.",
            ),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a .py file with the given arguments (if any), constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to be run, relative to the working directory. Can only use .py files.",
            ),
            "arguments" : types.Schema(
                type=types.Type.STRING, 
                description="A series of optional arguments for the python file in question. Defaults to None if none are given. If not specified, usually isnt neccessary."
            )
        }, 
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites data to a given file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to be edited, relative to the working directory.",
            ),
            "content" : types.Schema(
                type=types.Type.STRING,
                description="The new content to be written to the file."
            )
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]
)

callable_functions = {
    "get_files_info" : get_files_info,
    "get_file_content" : get_file_content,
    "run_python_file" : run_python_file,
    "write_file" : write_file
}

def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    if callable_functions.get(function_call_part.name):
        function_result = callable_functions[function_call_part.name]("./calculator", *(function_call_part.args.values()))
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": function_result},
                )
            ],
        )
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )
    


def main():
    
    load_dotenv()
    key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=key)
    user_prompt = sys.argv[1]
    messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    for i in range(20):
        response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt), 
        )
            
        for candidate in response.candidates:
            messages.append(candidate.content)
    
   
        if response.function_calls is not None:
            for function_call_part in response.function_calls:
                if type(function_call_part.name) == str:
                    if "--verbose" in sys.argv:
                        content = call_function(function_call_part, verbose=True)
                        if not content.parts[0].function_response.response:
                            raise Exception("man wtf")
                        print(f"-> {content.parts[0].function_response.response}")
                        messages.append(content)
                    else:
                        content = call_function(function_call_part)
                        messages.append(content)
                    

        else:
            if "--verbose" in sys.argv:
                print(f"User prompt: {user_prompt}")
                print(response.text)
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}\n"
                f"Response tokens: {response.usage_metadata.candidates_token_count}")
            else:
                print(response.text)
            break


if __name__ == '__main__':
    main()