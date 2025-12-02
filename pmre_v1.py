import cv2
import numpy as np


class PlanarMetricRectifier:
    """
    Planar Metric Rectification Engine (PMRE)
    
    A class for correcting perspective distortion in images of planar objects
    to enable precise metric measurements.
    """
    
    def __init__(self, src_points, dst_points):
        """
        Initialize the PlanarMetricRectifier with source and destination points.
        
        Parameters
        ----------
        src_points : array-like
            List of 4 [x, y] tuples representing points in the source image (pixels)
        dst_points : array-like
            List of 4 [x, y] tuples representing corresponding points in 
            real-world space (millimeters)
        """
        self.src_points = np.array(src_points, dtype=np.float32)
        self.dst_points = np.array(dst_points, dtype=np.float32)
        
        # Validate input shapes
        if self.src_points.shape[0] < 4:
            raise ValueError("At least 4 point correspondences are required")
        if self.src_points.shape[0] != self.dst_points.shape[0]:
            raise ValueError("src_points_px and dst_points_mm must have the same number of points")
        
        self.homography = None
        self.metric_scale = None
        
    def calculate_homography(self):
        """
        Calculate the homography matrix using RANSAC for robustness.
        
        Returns
        -------
        np.ndarray
            3x3 homography matrix
        """
        # Reshape points for OpenCV
        src_pts = self.src_points.reshape(-1, 1, 2)
        dst_pts = self.dst_points.reshape(-1, 1, 2)
        
        # Compute homography using RANSAC
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        if H is None:
            raise ValueError("Failed to compute homography matrix")
            
        # Normalize homography matrix
        H = H / H[2, 2]
        self.homography = H
        return H
    
    def rectify_image(self, image):
        """
        Rectify an image using the computed homography, preventing cropping.
        
        This method computes the appropriate output canvas size to ensure the
        entire transformed image is visible.
        
        Parameters
        ----------
        image : np.ndarray
            Input image to rectify
            
        Returns
        -------
        np.ndarray
            Rectified image with corrected perspective
        """
        if self.homography is None:
            self.calculate_homography()
            
        height, width = image.shape[:2]
        
        # Define the four corners of the input image
        corners = np.array([
            [0, 0],          # Top-left
            [width, 0],      # Top-right
            [width, height], # Bottom-right
            [0, height]      # Bottom-left
        ], dtype=np.float32)
        
        # Transform the corners using the homography
        transformed_corners = cv2.perspectiveTransform(
            corners.reshape(-1, 1, 2), self.homography
        ).reshape(-1, 2)
        
        # Find bounding box of the transformed corners
        min_x = np.min(transformed_corners[:, 0])
        max_x = np.max(transformed_corners[:, 0])
        min_y = np.min(transformed_corners[:, 1])
        max_y = np.max(transformed_corners[:, 1])
        
        # Calculate translation to move min coordinates to origin
        translate_x = -min_x
        translate_y = -min_y
        
        # Create translation matrix
        translation_matrix = np.array([
            [1, 0, translate_x],
            [0, 1, translate_y],
            [0, 0, 1]
        ], dtype=np.float32)
        
        # Compose final homography: translation * homography
        H_final = translation_matrix @ self.homography
        
        # Calculate output dimensions
        output_width = int(np.ceil(max_x - min_x))
        output_height = int(np.ceil(max_y - min_y))
        
        # Apply perspective transformation
        rectified_image = cv2.warpPerspective(
            image, H_final, (output_width, output_height),
            flags=cv2.INTER_LINEAR
        )
        
        return rectified_image
    
    def calculate_metric_scale(self, target_width_mm=210, target_height_mm=297):
        """
        Calculate the metric scale (pixels per millimeter).
        
        Parameters
        ----------
        target_width_mm : float
            Target width in millimeters
        target_height_mm : float
            Target height in millimeters
            
        Returns
        -------
        float
            Scale factor: pixels per millimeter
        """
        # Calculate distances in both spaces
        pixel_distances = []
        world_distances = []
        
        # Calculate pairwise distances
        for i in range(len(self.src_points)):
            for j in range(i+1, len(self.src_points)):
                # Distance in original pixel space
                pixel_dist = np.linalg.norm(self.src_points[i] - self.src_points[j])
                pixel_distances.append(pixel_dist)
                
                # Distance in world space (mm)
                world_dist = np.linalg.norm(self.dst_points[i] - self.dst_points[j])
                world_distances.append(world_dist)
        
        # Calculate scale as ratio of pixel distance to world distance
        scales = [p/w for p, w in zip(pixel_distances, world_distances) if w > 1e-10]
        
        if not scales:
            raise ValueError("Unable to compute metric scale: invalid point correspondences")
            
        # Return average scale
        self.metric_scale = np.mean(scales)
        return self.metric_scale