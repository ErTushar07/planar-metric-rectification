import cv2
import numpy as np
import sys
import os


def mouse_callback(event, x, y, flags, param):
    """Mouse callback function to capture clicks."""
    points = param['points']
    image = param['image']
    clone = param['clone']
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append([x, y])
            # Draw a circle at the clicked point
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
            # Draw a line connecting the points
            if len(points) > 1:
                cv2.line(image, tuple(points[-2]), tuple(points[-1]), (0, 255, 0), 2)
            cv2.imshow("Image", image)
            
            # If we have 4 points, draw the closing line
            if len(points) == 4:
                cv2.line(image, tuple(points[-1]), tuple(points[0]), (0, 255, 0), 2)
                cv2.imshow("Image", image)
                
                # Print the points in the required format
                filename = os.path.basename(param['filename'])
                points_array = np.array(points, dtype=np.float32)
                points_str = ', '.join([f'[{int(p[0])},{int(p[1])}]' for p in points_array])
                print(f'"{filename}": np.array([{points_str}], dtype=np.float32),')


def main():
    """Main function to handle command line arguments and run the coordinate picker."""
    if len(sys.argv) != 2:
        print("Usage: python get_coords.py <image_path>")
        sys.exit(1)
        
    image_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        sys.exit(1)
        
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image '{image_path}'.")
        sys.exit(1)
        
    clone = image.copy()
    
    # Store points and image reference
    points = []
    param = {'points': points, 'image': image, 'clone': clone, 'filename': image_path}
    
    # Create window and set mouse callback
    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", mouse_callback, param)
    
    # Display instructions
    print("Click on 4 corners of the planar object in clockwise or counter-clockwise order.")
    print("Press 'r' to reset points, 'q' to quit.")
    
    # Display image
    cv2.imshow("Image", image)
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        # Reset points if 'r' is pressed
        if key == ord("r"):
            image[:] = clone[:]
            points.clear()
            cv2.imshow("Image", image)
            print("Points reset. Click on 4 corners again.")
            
        # Quit if 'q' is pressed
        elif key == ord("q"):
            break
            
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()