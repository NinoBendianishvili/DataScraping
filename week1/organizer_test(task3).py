import os
import shutil
import time
import random
import string
from file_organizer import FileOrganizer

def create_test_environment(test_dir="test_files"):
    """Create a test directory with sample files of different types and sizes."""
    print(f"Creating test environment in '{test_dir}'...")
    
    # Remove test directory if it exists
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    # Create test directory
    os.makedirs(test_dir)
    
    # Create subdirectories
    os.makedirs(os.path.join(test_dir, "docs"))
    os.makedirs(os.path.join(test_dir, "images"))
    
    # Create various file types with different dates and sizes
    file_types = {
        "txt": ["report", "notes", "readme", "log", "data"],
        "csv": ["sales", "inventory", "customers"],
        "json": ["config", "settings", "data"],
        "jpg": ["photo", "screenshot", "image"],
        "pdf": ["document", "invoice", "report"],
        "py": ["script", "module", "test"]
    }
    
    created_files = []
    
    # Create files with various sizes and dates
    for ext, prefixes in file_types.items():
        for prefix in prefixes:
            # Create file in root test directory
            filename = f"{prefix}.{ext}"
            filepath = os.path.join(test_dir, filename)
            
            # Create files with random content and sizes (100B to 10KB)
            size = random.randint(100, 10240)
            with open(filepath, 'wb') as f:
                f.write(os.urandom(size))
            
            created_files.append(filepath)
            
            # Create some files in subdirectories
            if random.choice([True, False]):
                subdir = random.choice(["docs", "images"])
                subpath = os.path.join(test_dir, subdir, f"{prefix}_{subdir}.{ext}")
                with open(subpath, 'wb') as f:
                    f.write(os.urandom(size))
                created_files.append(subpath)
    
    # Create a few files with older modification times
    for i in range(3):
        filename = f"old_file_{i}.txt"
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"This is an older file {i}")
        
        # Set modification time to random time in past (1-30 days ago)
        days_ago = random.randint(1, 30)
        past_time = time.time() - (days_ago * 86400)  # 86400 seconds in a day
        os.utime(filepath, (past_time, past_time))
        
        created_files.append(filepath)
    
    print(f"Created {len(created_files)} test files")
    return created_files

def test_file_organizer():
    """Test the FileOrganizer class functionality."""
    # Set up test environment
    test_dir = "test_files"
    created_files = create_test_environment(test_dir)
    
    # Initialize the organizer
    organizer = FileOrganizer(test_dir)
    print("\n-------- Testing FileOrganizer --------")
    
    # Test 1: List files
    print("\n1. Testing list_files()...")
    files = organizer.list_files()
    print(f"Found {len(files)} files in root directory")
    
    # Test recursive file listing
    all_files = organizer.list_files(recursive=True)
    print(f"Found {len(all_files)} files recursively")
    
    # Test 2: File sorting
    print("\n2. Testing sort_files()...")
    # Sort by name
    sorted_by_name = organizer.sort_files(files, sort_by='name')
    print("First 3 files sorted by name:")
    for file in sorted_by_name[:3]:
        print(f"  - {os.path.basename(file)}")
    
    # Sort by type
    sorted_by_type = organizer.sort_files(files, sort_by='type')
    print("\nFirst 3 files sorted by type:")
    for file in sorted_by_type[:3]:
        print(f"  - {os.path.basename(file)}")
    
    # Sort by date
    sorted_by_date = organizer.sort_files(files, sort_by='date')
    print("\nFirst 3 files sorted by date:")
    for file in sorted_by_date[:3]:
        print(f"  - {os.path.basename(file)} - {time.ctime(os.path.getmtime(file))}")
    
    # Test 3: Get file info
    print("\n3. Testing get_file_info()...")
    sample_file = files[0]
    file_info = organizer.get_file_info(sample_file)
    print(f"Information for {os.path.basename(sample_file)}:")
    for key, value in file_info.items():
        print(f"  - {key}: {value}")
    
    # Test 4: Search files
    print("\n4. Testing search_files()...")
    # Search for files containing "report"
    report_files = organizer.search_files("report")
    print(f"Found {len(report_files)} files containing 'report':")
    for file in report_files:
        print(f"  - {os.path.basename(file)}")
    
    # Search with case sensitivity
    case_sensitive_results = organizer.search_files("REPORT", case_sensitive=True)
    print(f"\nFound {len(case_sensitive_results)} files containing 'REPORT' (case-sensitive)")
    
    # Test 5: Organize by type
    print("\n5. Testing organize_by_type()...")
    organized_dir = os.path.join(test_dir, "organized_by_type")
    os.makedirs(organized_dir, exist_ok=True)
    type_map = organizer.organize_by_type(target_dir=organized_dir)
    
    print("Files organized by type:")
    for ext, ext_files in type_map.items():
        print(f"  - {ext}: {len(ext_files)} files")
    
    # Test 6: Organize by date
    print("\n6. Testing organize_by_date()...")
    date_dir = os.path.join(test_dir, "organized_by_date")
    os.makedirs(date_dir, exist_ok=True)
    date_map = organizer.organize_by_date(target_dir=date_dir)
    
    print("Files organized by date:")
    for date_folder, date_files in date_map.items():
        print(f"  - {date_folder}: {len(date_files)} files")
    
    # Test 7: Organize by size
    print("\n7. Testing organize_by_size()...")
    size_dir = os.path.join(test_dir, "organized_by_size")
    os.makedirs(size_dir, exist_ok=True)
    size_map = organizer.organize_by_size(target_dir=size_dir)
    
    print("Files organized by size:")
    for size_category, size_files in size_map.items():
        print(f"  - {size_category}: {len(size_files)} files")
    
    # Test 8: Create backup
    print("\n8. Testing create_backup()...")
    backup_path = organizer.create_backup(source_dir=test_dir, backup_name="test_backup.zip")
    if os.path.exists(backup_path):
        backup_size = os.path.getsize(backup_path)
        print(f"Backup created successfully: {backup_path} ({backup_size} bytes)")
    else:
        print(f"Failed to create backup at {backup_path}")
    
    print("\n-------- All tests completed --------")

if __name__ == "__main__":
    test_file_organizer()