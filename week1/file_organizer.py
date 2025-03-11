import os
import shutil
import datetime
import logging
from collections import defaultdict
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='file_operations.log',
    filemode='a'
)

class FileOrganizer:
    def __init__(self, root_directory):
        self.root_directory = os.path.abspath(root_directory)
        if not os.path.exists(self.root_directory):
            os.makedirs(self.root_directory)
            logging.info(f"Created root directory: {self.root_directory}")
        logging.info(f"Initialized FileOrganizer with root directory: {self.root_directory}")

    def list_files(self, directory=None, recursive=False):
        if directory is None:
            directory = self.root_directory
        else:
            directory = os.path.abspath(directory)
            
        logging.info(f"Listing files in directory: {directory}, recursive={recursive}")
        
        file_list = []
        
        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_list.append(os.path.join(root, file))
        else:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    file_list.append(item_path)
                    
        logging.info(f"Found {len(file_list)} files")
        return file_list

    def get_file_info(self, file_path):
        if not os.path.isfile(file_path):
            logging.warning(f"File not found: {file_path}")
            return None
            
        stats = os.stat(file_path)
        file_info = {
            'name': os.path.basename(file_path),
            'path': os.path.abspath(file_path),
            'size': stats.st_size,
            'extension': os.path.splitext(file_path)[1].lower(),
            'created': datetime.datetime.fromtimestamp(stats.st_ctime),
            'modified': datetime.datetime.fromtimestamp(stats.st_mtime),
            'accessed': datetime.datetime.fromtimestamp(stats.st_atime)
        }
        
        return file_info

    def sort_files(self, files, sort_by='name', reverse=False):

        logging.info(f"Sorting files by {sort_by}, reverse={reverse}")
        
        if sort_by == 'name':
            return sorted(files, key=lambda x: os.path.basename(x).lower(), reverse=reverse)
        elif sort_by == 'type':
            return sorted(files, key=lambda x: os.path.splitext(x)[1].lower(), reverse=reverse)
        elif sort_by == 'date':
            return sorted(files, key=lambda x: os.path.getmtime(x), reverse=reverse)
        elif sort_by == 'size':
            return sorted(files, key=lambda x: os.path.getsize(x), reverse=reverse)
        else:
            logging.warning(f"Invalid sort criteria: {sort_by}. Using 'name' instead.")
            return sorted(files, key=lambda x: os.path.basename(x).lower(), reverse=reverse)

    def organize_by_type(self, source_dir=None, target_dir=None):

        if source_dir is None:
            source_dir = self.root_directory
        if target_dir is None:
            target_dir = self.root_directory
            
        logging.info(f"Organizing files by type from {source_dir} to {target_dir}")
        
        files = self.list_files(source_dir)
        extensions_map = defaultdict(list)
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext:
                ext = ext[1:]
                type_dir = os.path.join(target_dir, ext)
                
                if not os.path.exists(type_dir):
                    os.makedirs(type_dir)
                    logging.info(f"Created directory for {ext} files: {type_dir}")
                
                dest_file = os.path.join(type_dir, os.path.basename(file))
                shutil.copy2(file, dest_file)
                logging.info(f"Copied {file} to {dest_file}")
                extensions_map[ext].append(dest_file)
            else:

                no_ext_dir = os.path.join(target_dir, "no_extension")
                if not os.path.exists(no_ext_dir):
                    os.makedirs(no_ext_dir)
                    logging.info(f"Created directory for files with no extension: {no_ext_dir}")
                
                dest_file = os.path.join(no_ext_dir, os.path.basename(file))
                shutil.copy2(file, dest_file)
                logging.info(f"Copied {file} to {dest_file}")
                extensions_map["no_extension"].append(dest_file)
        
        return dict(extensions_map)

    def organize_by_date(self, source_dir=None, target_dir=None, date_format='%Y-%m'):

        if source_dir is None:
            source_dir = self.root_directory
        if target_dir is None:
            target_dir = self.root_directory
            
        logging.info(f"Organizing files by date from {source_dir} to {target_dir} using format {date_format}")
        
        files = self.list_files(source_dir)
        date_map = defaultdict(list)
        
        for file in files:
            creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file))
            date_folder = creation_time.strftime(date_format)
            date_dir = os.path.join(target_dir, date_folder)
            
            if not os.path.exists(date_dir):
                os.makedirs(date_dir)
                logging.info(f"Created directory for {date_folder}: {date_dir}")
            
            dest_file = os.path.join(date_dir, os.path.basename(file))
            shutil.copy2(file, dest_file)
            logging.info(f"Copied {file} to {dest_file}")
            date_map[date_folder].append(dest_file)
        
        return dict(date_map)

    def organize_by_size(self, source_dir=None, target_dir=None):

        if source_dir is None:
            source_dir = self.root_directory
        if target_dir is None:
            target_dir = self.root_directory
            
        logging.info(f"Organizing files by size from {source_dir} to {target_dir}")
        
        files = self.list_files(source_dir)
        size_map = defaultdict(list)
        

        size_categories = {
            "tiny": (0, 10 * 1024),  # 0 - 10 KB
            "small": (10 * 1024, 1 * 1024 * 1024),  # 10 KB - 1 MB
            "medium": (1 * 1024 * 1024, 100 * 1024 * 1024),  # 1 MB - 100 MB
            "large": (100 * 1024 * 1024, 1 * 1024 * 1024 * 1024),  # 100 MB - 1 GB
            "huge": (1 * 1024 * 1024 * 1024, float('inf'))  # > 1 GB
        }
        
        for file in files:
            file_size = os.path.getsize(file)
            category = None
            
            for cat_name, (min_size, max_size) in size_categories.items():
                if min_size <= file_size < max_size:
                    category = cat_name
                    break
            
            if category:
                size_dir = os.path.join(target_dir, category)
                if not os.path.exists(size_dir):
                    os.makedirs(size_dir)
                    logging.info(f"Created directory for {category} files: {size_dir}")
                
                dest_file = os.path.join(size_dir, os.path.basename(file))
                shutil.copy2(file, dest_file)
                logging.info(f"Copied {file} to {dest_file}")
                size_map[category].append(dest_file)
        
        return dict(size_map)

    def search_files(self, search_term, directory=None, recursive=True, case_sensitive=False):

        if directory is None:
            directory = self.root_directory
            
        logging.info(f"Searching for '{search_term}' in {directory}, recursive={recursive}, case_sensitive={case_sensitive}")
        
        files = self.list_files(directory, recursive=recursive)
        matching_files = []
        
        if not case_sensitive:
            pattern = re.compile(re.escape(search_term), re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(search_term))
            
        for file in files:
            filename = os.path.basename(file)
            if pattern.search(filename):
                matching_files.append(file)
                
        logging.info(f"Found {len(matching_files)} files matching '{search_term}'")
        return matching_files

    def create_backup(self, source_dir=None, backup_name=None):

        if source_dir is None:
            source_dir = self.root_directory
            
        if backup_name is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.zip"
            
        backup_path = os.path.join(os.path.dirname(source_dir), backup_name)
        
        logging.info(f"Creating backup of {source_dir} to {backup_path}")
        
        shutil.make_archive(
            os.path.splitext(backup_path)[0],  
            'zip',
            source_dir
        )
        
        logging.info(f"Backup created: {backup_path}")
        return backup_path


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