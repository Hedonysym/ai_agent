import ast

def count_functions(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
    tree = ast.parse(content)
    function_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_count += 1
    return function_count

if __name__ == "__main__":
    num_functions = count_functions('tests.py')
    print(num_functions)