import os
import ast
import subprocess

import struct


def get_local_imports(file_path):
    """Parse a Python file and extract local imports, including `from foo import bar` idiom."""
    local_imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        local_imports.append(module_name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:  # Handles `from foo import bar`
                        module_name = node.module.split('.')[0]
                        local_imports.append(module_name)
                    elif node.level > 0:  # Handles relative imports
                        local_imports.append("")  # Add an empty string for relative imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")

    # Filter out empty and duplicate entries
    filtered_imports_list = list(filter(None, set(local_imports)))
    print(filtered_imports_list)
    return filtered_imports_list


def resolve_local_module(module_name, base_dir):
    """Resolve a local module to its file path."""
    py_file = os.path.join(base_dir, f"{module_name}.py")
    init_file = os.path.join(base_dir, module_name, "__init__.py")

    if os.path.isfile(py_file):
        return py_file
    elif os.path.isfile(init_file):
        return init_file
    return None


def generate_cfg(file_path):
    """Generate a control flow graph for a Python file using code2flow."""
    output_file = f"{os.path.basename(file_path).replace('.py', 'CFG.png')}"
    subprocess.run(["code2flow", file_path, "--output", output_file], check=True)
    print(f"Generated CFG for {file_path} -> {output_file}")


def process_entry_point(entry_point, visited=set()):
    """Recursively process an entry point and its local imports."""
    if entry_point in visited:
        return
    visited.add(entry_point)

    # Generate CFG for the entry point
    generate_cfg(entry_point)

    # Get local imports and process them recursively
    base_dir = os.path.dirname(entry_point)
    for module in get_local_imports(entry_point):
        module_path = resolve_local_module(module, base_dir)
        if module_path and module_path not in visited:
            process_entry_point(module_path, visited)






















def cleanup_gv_files():
    """Deletes all .gv files in the current working directory."""
    cwd = os.getcwd()
    gv_files = [file for file in os.listdir(cwd) if file.endswith('.gv')]

    for gv_file in gv_files:
        try:
            os.remove(gv_file)
            print(f"Deleted: {gv_file}")
        except Exception as e:
            print(f"Error deleting {gv_file}: {e}")

def cleanup_empty_graphs():
    """Deletes all ..CFG.png files in the current directory if their width is less than 500px."""
    cwd = os.getcwd()
    png_files = [file for file in os.listdir(cwd) if file.endswith("CFG.png")]

    from PIL import Image
    for png_file in png_files:
        try:
            width = Image.open(png_file).width
            if width and width < 500:
                os.remove(png_file)
                print(f"Deleted: {png_file} (width: {width}px)")
        except Exception as e:
            print(f"Error processing {png_file}: {e}")














if __name__ == "__main__":
    # Hardcoded paths
    entry_point = os.path.abspath("../bot.py")

    process_entry_point(entry_point)

    cleanup_gv_files()

    cleanup_empty_graphs()
    
