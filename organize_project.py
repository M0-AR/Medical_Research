import os
import shutil
from pathlib import Path

# Directories to ignore
IGNORE_DIRS = {'venv', '__pycache__', '.git', 'node_modules', 'frontend', 'backend'}

def find_python_imports(file_path):
    """Find all Python imports in a file."""
    imports = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # Remove 'import' and 'from' keywords and get the base module
                if line.startswith('from '):
                    module = line.split()[1].split('.')[0]
                else:
                    module = line.split()[1].split('.')[0]
                imports.add(module)
    return imports

def find_all_python_files(src_dir):
    """Find all Python files in the directory."""
    python_files = set()
    test_files = set()
    
    for root, dirs, files in os.walk(src_dir):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                if file.startswith('test_'):
                    test_files.add(full_path)
                else:
                    python_files.add(full_path)
    
    return python_files, test_files

def find_related_files(start_file, src_dir):
    """Find all related Python files starting from the main file."""
    related_files = set()
    processed_files = set()
    files_to_process = {start_file}
    
    # Get all Python files first
    python_files, test_files = find_all_python_files(src_dir)
    
    # Add all test files to related files
    related_files.update(test_files)
    
    while files_to_process:
        current_file = files_to_process.pop()
        if current_file in processed_files:
            continue
            
        processed_files.add(current_file)
        if os.path.exists(current_file):
            related_files.add(current_file)
            
            # Find imports in this file
            imports = find_python_imports(current_file)
            
            # Look for related Python files
            for py_file in python_files:
                if os.path.basename(py_file).replace('.py', '') in imports:
                    files_to_process.add(py_file)
    
    return related_files

def create_new_structure(source_files, target_dir):
    """Create the new project structure and copy files."""
    # Create main directories
    structure = {
        'src': {
            'core': [],
            'models': [],
            'scrapers': [],
            'utils': []
        },
        'tests': [],
        'config': [],
        'results': []
    }
    
    # Create directories
    target_dir = Path(target_dir)
    for main_dir, sub_dirs in structure.items():
        main_path = target_dir / main_dir
        main_path.mkdir(parents=True, exist_ok=True)
        
        if isinstance(sub_dirs, list):
            # Create __init__.py
            (main_path / '__init__.py').touch()
        else:
            for sub_dir in sub_dirs:
                sub_path = main_path / sub_dir
                sub_path.mkdir(parents=True, exist_ok=True)
                (sub_path / '__init__.py').touch()
    
    # Copy requirements.txt if it exists
    if os.path.exists('requirements.txt'):
        shutil.copy2('requirements.txt', target_dir / 'requirements.txt')
        print("Copied requirements.txt")
    
    # Copy .env if it exists
    if os.path.exists('.env'):
        shutil.copy2('.env', target_dir / '.env')
        print("Copied .env")
    
    # Categorize and copy files
    for file_path in source_files:
        file_name = os.path.basename(file_path)
        
        # Skip __init__.py files
        if file_name == '__init__.py':
            continue
            
        # Determine target directory based on file name or content
        if file_name.startswith('test_'):
            target_subdir = target_dir / 'tests'
        elif 'config' in file_name.lower():
            target_subdir = target_dir / 'config'
        elif 'scraper' in file_name.lower():
            target_subdir = target_dir / 'src' / 'scrapers'
        elif 'analyzer' in file_name.lower():
            target_subdir = target_dir / 'src' / 'core'
        elif 'llm' in file_name.lower():
            target_subdir = target_dir / 'src' / 'models'
        else:
            target_subdir = target_dir / 'src' / 'utils'
        
        # Copy the file
        shutil.copy2(file_path, target_subdir / file_name)
        print(f"Copied {file_name} to {target_subdir.name}")

def main():
    # Source directory (current project)
    src_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find the main analyzer file
    main_file = os.path.join(src_dir, 'paper_analyzer.py')
    
    if not os.path.exists(main_file):
        print(f"Error: Could not find {main_file}")
        return
        
    # Find all related files
    print("Finding related files...")
    related_files = find_related_files(main_file, src_dir)
    
    if not related_files:
        print("No related files found!")
        return
        
    print(f"\nFound {len(related_files)} related files")
    
    # Create new project structure
    target_dir = os.path.join(src_dir, 'research_analyzer_last')
    print(f"\nCreating new project structure in {target_dir}...")
    create_new_structure(related_files, target_dir)
    
    print("\nProject reorganization complete!")
    print(f"New project structure created in: {target_dir}")

if __name__ == '__main__':
    main()
