import os
import shutil
import glob


def main():
    # Define the target list of files we need
    target_files = {
        "IMG_7282.jpg",
        "IMG_7284.jpg",
        "IMG_7286.jpg",
        "IMG_7288.jpg",
        "IMG_7290.jpg",
        "IMG_7292.jpg",
        "IMG_7294.jpg",
        "IMG_7296.jpg"
    }
    
    # Check if input_images directory exists, create if not
    if not os.path.exists("input_images"):
        os.makedirs("input_images")
        print("📁 Created input_images directory")
    
    # Look for files in current directory and raw_data folder (including subdirectories) if it exists
    search_paths = ["."]
    if os.path.exists("raw_data"):
        search_paths.append("raw_data")
        # Also search subdirectories of raw_data
        for root, dirs, files in os.walk("raw_data"):
            for d in dirs:
                search_paths.append(os.path.join(root, d))
    
    # Dictionary to store found files
    found_files = {}
    
    # Search for target files
    for path in search_paths:
        # Search for all jpg files in the directory
        jpg_files = glob.glob(os.path.join(path, "*.jpg"))
        
        # Check each jpg file
        for file_path in jpg_files:
            filename = os.path.basename(file_path)
            
            # Check if this is one of our target files (exact match, not duplicates)
            if filename in target_files and filename not in found_files:
                # Make sure it's not a duplicate/renamed file (e.g., IMG_7282-1.jpg)
                name_part = filename.split('.')[0]
                if '-' not in name_part:
                    found_files[filename] = file_path
    
    # Copy files to input_images directory
    copied_count = 0
    missing_files = []
    
    for target_file in sorted(target_files):
        if target_file in found_files:
            source_path = found_files[target_file]
            destination_path = os.path.join("input_images", target_file)
            
            try:
                shutil.copy2(source_path, destination_path)
                print(f"✅ Copied {target_file}")
                copied_count += 1
            except Exception as e:
                print(f"❌ Error copying {target_file}: {e}")
                missing_files.append(target_file)
        else:
            print(f"❌ Missing {target_file}")
            missing_files.append(target_file)
    
    # Print summary
    print(f"\n📊 Summary: {copied_count} files copied, {len(missing_files)} files missing")
    
    if missing_files:
        print("Missing files:", ", ".join(missing_files))


if __name__ == "__main__":
    main()