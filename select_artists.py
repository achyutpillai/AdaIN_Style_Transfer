import pandas as pd
import os
import shutil
import re
import sys
import unicodedata # Import unicodedata

# --- Configuration --- START ---

# 1. PATH to the artists.csv file
ARTISTS_CSV_PATH = 'data/artists.csv' # <<< MODIFY THIS

# 2. PATH to the directory containing the ARTIST SUBFOLDERS
IMAGE_SOURCE_PARENT_DIR = 'data/images' # <<< MODIFY THIS

# 3. PATH to the directory where you want to SAVE the selected images
OUTPUT_DIR = 'data/selected_styles' # <<< MODIFY THIS (can be relative or absolute)

# 4. List of target artist names (ensure spelling matches artists.csv)
TARGET_ARTISTS = [
    "Vasiliy Kandinskiy",
    "Claude Monet",
    "Salvador Dali",
    "Vincent van Gogh",
    "Gustav Klimt",
    "Hieronymus Bosch",
    "Pablo Picasso",
    "Henri Matisse",
    "Edvard Munch",
    "Georges Seurat",
    "Piet Mondrian",
    "Jackson Pollock",
    "Frida Kahlo",
    "William Turner",
    "Albrecht Dürer"  # Ensure this matches CSV, script will normalize 'ü'
]

# --- Configuration --- END ---


def sanitize_foldername(name):
    """
    Attempts to convert an artist name from the CSV to a likely folder name.
    Includes Unicode normalization (NFC form).
    """
    # Normalize the name first (handles variations in character representation)
    normalized_name = unicodedata.normalize('NFC', name)
    # Replace spaces with underscores
    folder_name = normalized_name.replace(' ', '_')
    # Remove characters potentially unsafe for some filesystems if needed
    # folder_name = re.sub(r'[<>:"/\\|?*.]', '', folder_name)
    return folder_name

def check_paths():
    """Validate configured input paths."""
    if not os.path.isfile(ARTISTS_CSV_PATH):
        print(f"Error: artists.csv not found at '{ARTISTS_CSV_PATH}'")
        print("Please check the ARTISTS_CSV_PATH variable.")
        sys.exit(1)
    if not os.path.isdir(IMAGE_SOURCE_PARENT_DIR):
        print(f"Error: Image source parent directory not found at '{IMAGE_SOURCE_PARENT_DIR}'")
        print("This directory should contain the individual artist folders.")
        print("Please check the IMAGE_SOURCE_PARENT_DIR variable.")
        sys.exit(1)
    print("Input paths seem valid.")

def main():
    """Main function to execute the script logic."""
    print("Starting artist image selection script...")
    check_paths()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: '{os.path.abspath(OUTPUT_DIR)}'")

    # Read the CSV file with explicit UTF-8 encoding
    try:
        artists_df = pd.read_csv(ARTISTS_CSV_PATH, encoding='utf-8')
        artists_df['name'] = artists_df['name'].str.strip()
        print(f"Successfully loaded artists.csv ({len(artists_df)} total artists using UTF-8)")
    except Exception as e:
        print(f"Error reading CSV file '{ARTISTS_CSV_PATH}' with UTF-8: {e}")
        sys.exit(1) # Exit if initial read fails


    present_artists_df = artists_df[artists_df['name'].isin(TARGET_ARTISTS)]
    found_names = set(present_artists_df['name'])
    missing_names_in_csv = [name for name in TARGET_ARTISTS if name not in found_names]

    print(f"\nFound {len(present_artists_df)}/{len(TARGET_ARTISTS)} requested artists listed in the CSV.")
    if missing_names_in_csv:
        print("---")
        print("Warning: The following requested artists were NOT found in artists.csv:")
        for name in missing_names_in_csv:
            print(f" - '{name}' (Check spelling/details against the CSV)")
        print("---")
    if len(present_artists_df) == 0:
        print("Error: No matching artists found in CSV based on TARGET_ARTISTS list. Exiting.")
        sys.exit(1)

    # Get directory names from filesystem for comparison
    actual_folders_on_disk = {}
    try:
        print(f"\nScanning '{IMAGE_SOURCE_PARENT_DIR}' for actual folder names...")
        for item in os.listdir(IMAGE_SOURCE_PARENT_DIR):
             item_path = os.path.join(IMAGE_SOURCE_PARENT_DIR, item)
             if os.path.isdir(item_path):
                 # Store the normalized name mapping to the original name
                 normalized_name = unicodedata.normalize('NFC', item)
                 actual_folders_on_disk[normalized_name] = item # Key: normalized, Value: original
        print(f"Found {len(actual_folders_on_disk)} directories.")
    except Exception as e:
        print(f"Error listing source directory contents: {e}")
        sys.exit(1)

    print("\nAttempting to copy image folders using normalized comparison...")
    copied_folders = 0
    skipped_folders = 0

    for index, artist_row in present_artists_df.iterrows():
        artist_name_csv = artist_row['name']
        # Generate the expected folder name from CSV name (sanitized & normalized)
        expected_folder_name_normalized = sanitize_foldername(artist_name_csv)

        print(f" -> Processing '{artist_name_csv}' (Normalized expected folder: '{expected_folder_name_normalized}')")

        # Check if the normalized expected name exists in the actual folders found
        if expected_folder_name_normalized in actual_folders_on_disk:
            # Get the original (non-normalized) folder name as it exists on disk
            original_folder_name = actual_folders_on_disk[expected_folder_name_normalized]
            source_artist_folder = os.path.join(IMAGE_SOURCE_PARENT_DIR, original_folder_name)
            # Use the original folder name for the destination as well
            destination_artist_folder = os.path.join(OUTPUT_DIR, original_folder_name)

            print(f"Found matching folder on disk: '{original_folder_name}'")
            try:
                shutil.copytree(source_artist_folder, destination_artist_folder, dirs_exist_ok=True)
                num_files_copied = len([f for f in os.listdir(destination_artist_folder) if os.path.isfile(os.path.join(destination_artist_folder, f))])
                print(f"Successfully copied {num_files_copied} file(s) to '{destination_artist_folder}'")
                copied_folders += 1
            except Exception as e:
                print(f"ERROR copying folder for '{artist_name_csv}' ('{original_folder_name}'): {e}")
                skipped_folders += 1
        else:
            print(f"WARNING: Normalized folder name '{expected_folder_name_normalized}' NOT FOUND among actual disk folders. Skipping.")
            skipped_folders += 1


    print("\n--------------------")
    print("Script finished.")
    print(f"Processed {len(present_artists_df)} artists found in CSV.")
    print(f"Successfully copied folders for {copied_folders} artists.")
    print(f"Skipped {skipped_folders} artists (folder not found or copy error).")
    print(f"Selected images are located in: '{os.path.abspath(OUTPUT_DIR)}'")
    print("--------------------")

if __name__ == "__main__":
    try:
        import pandas
    except ImportError:
        print("Error: pandas library not found. Please install it using:")
        print("pip install pandas")
        sys.exit(1)
    import unicodedata

    main()