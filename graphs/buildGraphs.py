import asyncio
import os
import ast
import subprocess
import sys
import time

from PIL import Image


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

    return list(filter(None, set(local_imports)))


def resolve_local_module(module_name, base_dir):
    """Resolve a local module to its file path."""
    py_file = os.path.join(base_dir, f"{module_name}.py")
    init_file = os.path.join(base_dir, module_name, "__init__.py")

    if os.path.isfile(py_file):
        return py_file
    elif os.path.isfile(init_file):
        return init_file
    return None



def collect_files(entry_point):
    """Collect all files that need processing starting from an entry point."""
    to_visit = [os.path.abspath(entry_point)]
    visited = set()
    files = []

    while to_visit:
        current_file = to_visit.pop()
        if current_file in visited:
            continue
        visited.add(current_file)
        files.append(current_file)

        base_dir = os.path.dirname(current_file)
        for module in get_local_imports(current_file):
            module_path = resolve_local_module(module, base_dir)
            if module_path and module_path not in visited:
                to_visit.append(module_path)

    return files





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

    for png_file in png_files:
        try:
            width = Image.open(png_file).width
            if width and width < 500:
                os.remove(png_file)
                print(f"Deleted: {png_file} (width: {width}px)")
        except Exception as e:
            print(f"Error processing {png_file}: {e}")



def generate_cfg(file_path):
    start_time = time.time()
    """Generate a control flow graph for a Python file using code2flow."""
    output_file = f"{os.path.basename(file_path).replace('.py', 'CFG.png')}"
    subprocess.run(
        ["code2flow", file_path, "--output", output_file],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print(f"Generated CFG for {file_path} -> {output_file}")
    return {file_path: time.time() - start_time}

async def process_files(files):
    """Process all collected files"""
    tasks = [asyncio.to_thread(generate_cfg, file_path) for file_path in files]
    runtimes = await asyncio.gather(*tasks)
    return runtimes

async def main():
    start_time = time.time()
    entry_point = os.path.abspath("../bot.py")

    if len(sys.argv) > 1:
        dragged_file = sys.argv[1]
        if os.path.isfile(dragged_file):  # Ensure the provided path is a file
            entry_point = os.path.abspath(dragged_file)

    # Step 1: Collect files
    files = collect_files(entry_point)
    print(f"Collected files: {files}\n")
    file_collection_end_time = time.time()

    # Step 2: Process files and get runtimes
    runtimes = await process_files(files)
    file_processing_end_time = time.time()
    print("")

    # Step 3: Cleanup
    cleanup_start_time = time.time()
    cleanup_gv_files()
    cleanup_empty_graphs()
    cleanup_end_time = time.time()

    # Calculate runtime segments
    total_runtime = cleanup_end_time - start_time
    file_collection_time = file_collection_end_time - start_time
    file_processing_time = file_processing_end_time - file_collection_end_time
    cleanup_time = cleanup_end_time - cleanup_start_time

    # Print individual runtimes for each file
    lines = []
    for runtime in runtimes:
        for file_path, duration in runtime.items():
            lines.append(f"\n   {round(duration, 2)}s ({os.path.getsize(file_path):,}B)   {os.path.basename(file_path)}")

    print("\nIndividual file runtimes:", "".join(lines))

    # Print total runtime breakdown
    print(f"\nTotal runtime: {round(total_runtime, 2)}s",
        f"\n    File collection: {round(file_collection_time, 2)}s",
        f"\n    File processing: {round(file_processing_time, 2)}s",
        f"\n    Cleanup: {round(cleanup_time, 2)}s"
    )


if __name__ == "__main__":
    asyncio.run(main())
    close_me = input("\nenter to close")