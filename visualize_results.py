import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from main import IMAGE_DATA


def draw_grid(image, grid_size=50):
    """
    Draw a grid overlay on the image.
    
    Parameters
    ----------
    image : np.ndarray
        Input image
    grid_size : int
        Size of grid cells in pixels
        
    Returns
    -------
    np.ndarray
        Image with grid overlay
    """
    # Create a copy of the image
    img_with_grid = image.copy()
    
    # Get image dimensions
    height, width = img_with_grid.shape[:2]
    
    # Draw vertical lines
    for x in range(0, width, grid_size):
        cv2.line(img_with_grid, (x, 0), (x, height), (0, 255, 0), 1, cv2.LINE_AA)
    
    # Draw horizontal lines
    for y in range(0, height, grid_size):
        cv2.line(img_with_grid, (0, y), (width, y), (0, 255, 0), 1, cv2.LINE_AA)
        
    return img_with_grid


def visualize_results():
    """
    Visualize the results of the Planar Metric Rectification Engine.
    
    This function displays the first 3 rectified images with their original counterparts,
    showing corner points on the original and grid overlays on the rectified images.
    """
    # Get list of rectified images
    output_folder = "output_images"
    rectified_files = [f for f in os.listdir(output_folder) if f.startswith("rectified_")]
    
    # Take only the first 3 images
    rectified_files = rectified_files[:3]
    
    if not rectified_files:
        print("No rectified images found in output_images folder.")
        return
    
    # Process each of the first 3 images
    for i, rectified_filename in enumerate(rectified_files):
        # Extract original filename
        original_filename = rectified_filename.replace("rectified_", "")
        
        # Load original and rectified images
        original_path = os.path.join("input_images", original_filename)
        rectified_path = os.path.join(output_folder, rectified_filename)
        
        original_img = cv2.imread(original_path)
        rectified_img = cv2.imread(rectified_path)
        
        if original_img is None or rectified_img is None:
            print(f"Could not load images for {original_filename}")
            continue
            
        # Convert BGR to RGB for matplotlib
        original_img_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        rectified_img_rgb = cv2.cvtColor(rectified_img, cv2.COLOR_BGR2RGB)
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Plot original image with corner points
        ax1.imshow(original_img_rgb)
        ax1.set_title(f"Original: {original_filename}")
        ax1.axis('off')
        
        # Plot corner points if available
        if original_filename in IMAGE_DATA and IMAGE_DATA[original_filename] is not None:
            points = np.array(IMAGE_DATA[original_filename])
            ax1.scatter(points[:, 0], points[:, 1], c='red', s=50, marker='x')
            # Connect points to form a polygon
            points_closed = np.vstack([points, points[0]])
            ax1.plot(points_closed[:, 0], points_closed[:, 1], 'r--', linewidth=1)
        
        # Plot rectified image with grid overlay
        rectified_with_grid = draw_grid(rectified_img_rgb)
        ax2.imshow(rectified_with_grid)
        ax2.set_title(f"Rectified: {rectified_filename}")
        ax2.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        print(f"Displaying results for {original_filename} ({i+1}/3)")


if __name__ == "__main__":
    visualize_results()