import os
import winreg
import psutil
from pathlib import Path

def get_size(path):
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += get_size(entry.path)
    except (PermissionError, FileNotFoundError):
        return 0
    return total

def convert_bytes(bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} GB"

def get_installed_programs():
    programs = []
    paths = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.expanduser("~\AppData\Local"),
        os.path.expanduser("~\AppData\Roaming"),
    ]
    
    print("\nAnalyzing installed applications...")
    print("This might take a few minutes...\n")
    
    for path in paths:
        if os.path.exists(path):
            try:
                for item in os.scandir(path):
                    if item.is_dir():
                        size = get_size(item.path)
                        if size > 100 * 1024 * 1024:  # Only show items larger than 100MB
                            programs.append({
                                'name': item.name,
                                'path': item.path,
                                'size': size,
                                'size_readable': convert_bytes(size)
                            })
            except PermissionError:
                continue

    # Sort by size (largest first)
    programs.sort(key=lambda x: x['size'], reverse=True)
    return programs

def main():
    programs = get_installed_programs()
    
    print("Largest Applications and Folders:")
    print("-" * 100)
    print(f"{'Size':>10} | {'Location':<30} | {'Name'}")
    print("-" * 100)
    
    for prog in programs:
        print(f"{prog['size_readable']:>10} | {os.path.dirname(prog['path']):<30} | {prog['name']}")

if __name__ == "__main__":
    main()
