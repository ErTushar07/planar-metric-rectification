import cv2
import numpy as np
import os
from pmre_v1 import PlanarMetricRectifier


# Define image data dictionary with filenames as keys
# Values should be filled with coordinate data obtained from get_coords.py
IMAGE_DATA = {
    "IMG_7282.jpg": [[100, 100], [500, 120], [480, 400], [80, 380]],  # Sample coordinates
    "IMG_7284.jpg": [[150, 120], [520, 100], [500, 380], [130, 400]],  # Sample coordinates
    "IMG_7286.jpg": [[120, 110], [510, 130], [490, 390], [110, 370]],  # Sample coordinates
    "IMG_7288.jpg": [[90, 130], [480, 110], [460, 370], [70, 390]],   # Sample coordinates
    "IMG_7290.jpg": None,  # TODO: Run get_coords.py to fill this
    "IMG_7292.jpg": None,  # TODO: Run get_coords.py to fill this
    "IMG_7294.jpg": None,  # TODO: Run get_coords.py to fill this
    "IMG_7296.jpg": None,  # TODO: Run get_coords.py to fill this
}

# Define target dimensions (A4 paper size in mm)
TARGET_WIDTH_MM = 210
TARGET_HEIGHT_MM = 297


def main():
    """Main function to process all images in the input folder."""
    input_folder = "input_images"
    output_folder = "output_images"
    
    # Counter for processed images
    processed_count = 0
    
    # Process each image in the IMAGE_DATA dictionary
    for filename, coords in IMAGE_DATA.items():
        # Skip if coordinates are not provided
        if coords is None:
            print(f"Warning: Skipping {filename} - No coordinates provided")
            continue
            
        # Construct full file path
        input_path = os.path.join(input_folder, filename)
        
        # Check if file exists
        if not os.path.exists(input_path):
            print(f"Warning: File {input_path} not found")
            continue
            
        # Load the image
        image = cv2.imread(input_path)
        if image is None:
            print(f"Error: Could not load image {input_path}")
            continue
            
        try:
            # Define destination points based on target dimensions
            # Assuming the coordinates form a rectangle, we map to the target size
            dst_points = np.array([
                [0, 0],                           # Top-left
                [TARGET_WIDTH_MM, 0],             # Top-right
                [TARGET_WIDTH_MM, TARGET_HEIGHT_MM], # Bottom-right
                [0, TARGET_HEIGHT_MM]             # Bottom-left
            ], dtype=np.float32)
            
            # Create the rectifier
            rectifier = PlanarMetricRectifier(coords, dst_points)
            
            # Rectify the image
            rectified_image = rectifier.rectify_image(image)
            
            # Calculate metric scale
            scale = rectifier.calculate_metric_scale()
            
            # Save the rectified image
            output_filename = f"rectified_{filename}"
            output_path = os.path.join(output_folder, output_filename)
            cv2.imwrite(output_path, rectified_image)
            
            # Print results
            print(f"Processed {filename}:")
            print(f"  - Saved as {output_filename}")
            print(f"  - Metric scale: {scale:.2f} pixels/mm")
            print()
            
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
            
    print(f"Processing complete. {processed_count} images processed successfully.")


if __name__ == "__main__":
    main()