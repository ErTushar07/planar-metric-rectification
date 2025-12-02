Planar Metric Rectification Engine (PMRE) Project
===============================================

This project processes a batch of manufacturing images to correct perspective distortion and enable precise metric measurements.

Project Structure:
------------------
- input_images/     : Place your JPG images here
- output_images/    : Rectified images will be saved here
- pmre_v1.py        : Core engine with PlanarMetricRectifier class
- get_coords.py     : Helper tool to manually select 4 corners on an image
- main.py           : Driver script to process all images

Usage Instructions:
-------------------

1. Place your images in the input_images/ folder
   Supported filenames:
   - IMG_7282.jpg, IMG_7284.jpg, IMG_7286.jpg, IMG_7288.jpg
   - IMG_7290.jpg, IMG_7292.jpg, IMG_7294.jpg, IMG_7296.jpg

2. For each image, run the coordinate picker tool:
   python get_coords.py input_images/IMG_7282.jpg
   
   Click on 4 corners of the planar object in the image.
   Copy the printed coordinates and paste them into main.py IMAGE_DATA.

3. Update the IMAGE_DATA dictionary in main.py with the coordinates.

4. Run the main processing script:
   python main.py

The rectified images will be saved in output_images/ with "rectified_" prefix.
Each processed image will display its metric scale (pixels per mm).