import pytest
import numpy as np
import cv2
from pmre_v1 import PlanarMetricRectifier


def test_initialization_invalid_inputs():
    """
    Test 1 (Initialization): Check that invalid inputs (e.g., only 3 points) raise an error.
    """
    # Test with only 3 points (should raise ValueError)
    src_points = [[0, 0], [1, 0], [1, 1]]
    dst_points = [[0, 0], [1, 0], [1, 1]]
    
    with pytest.raises(ValueError, match="At least 4 point correspondences are required"):
        PlanarMetricRectifier(src_points, dst_points)
    
    # Test with mismatched number of points
    src_points = [[0, 0], [1, 0], [1, 1], [0, 1]]
    dst_points = [[0, 0], [1, 0], [1, 1]]
    
    with pytest.raises(ValueError, match="src_points_px and dst_points_mm must have the same number of points"):
        PlanarMetricRectifier(src_points, dst_points)


def test_synthetic_square():
    """
    Test 2 (Synthetic Square): Create a synthetic 100x100 square, warp it using a known matrix,
    and check if PlanarMetricRectifier can recover the original 100x100 aspect ratio.
    """
    # Create a 100x100 square in world coordinates (mm)
    dst_points_mm = np.array([
        [0, 0],      # Bottom-left
        [100, 0],    # Bottom-right
        [100, 100],  # Top-right
        [0, 100]     # Top-left
    ], dtype=np.float32)
    
    # Define a perspective transformation matrix (simulating a camera view)
    # This creates a synthetic "tilted" view of the square
    H_warp = np.array([
        [1.5, 0.3, 50],
        [0.2, 1.2, 30],
        [0.001, 0.002, 1]
    ], dtype=np.float32)
    
    # Transform the square points using the warping matrix
    src_points_px = []
    for point in dst_points_mm:
        # Convert to homogeneous coordinates
        pt_homogeneous = np.array([point[0], point[1], 1], dtype=np.float32)
        # Apply transformation
        transformed = H_warp @ pt_homogeneous
        # Convert back to Cartesian coordinates
        x = transformed[0] / transformed[2]
        y = transformed[1] / transformed[2]
        src_points_px.append([x, y])
    
    src_points_px = np.array(src_points_px, dtype=np.float32)
    
    # Create the rectifier with the warped points and original square
    rectifier = PlanarMetricRectifier(src_points_px, dst_points_mm)
    
    # Calculate homography
    H_recovered = rectifier.calculate_homography()
    
    # Transform source points using the recovered homography
    src_points_homogeneous = np.hstack([src_points_px, np.ones((src_points_px.shape[0], 1))])
    transformed_points = (H_recovered @ src_points_homogeneous.T).T
    transformed_points = transformed_points[:, :2] / transformed_points[:, 2:3]
    
    # Check that transformed points closely match the destination points
    # Allow for some numerical error
    np.testing.assert_allclose(transformed_points, dst_points_mm, rtol=1e-2, atol=1)


def test_metric_scale():
    """
    Test 3 (Metric Scale): Assert that the calculated scale matches the known pixels/mm ratio within 1% tolerance.
    """
    # Create a rectangle with known dimensions: 200mm x 100mm
    dst_points_mm = np.array([
        [0, 0],      # Bottom-left
        [200, 0],    # Bottom-right
        [200, 100],  # Top-right
        [0, 100]     # Top-left
    ], dtype=np.float32)
    
    # Create source points directly in pixel space with a known scale
    # If we want a scale of 2 pixels/mm, then:
    # - 200mm becomes 400 pixels
    # - 100mm becomes 200 pixels
    src_points_px = np.array([
        [100, 50],   # Bottom-left
        [500, 50],   # Bottom-right (400 pixels wide)
        [500, 250],  # Top-right (200 pixels tall)
        [100, 250]   # Top-left
    ], dtype=np.float32)
    
    # Create the rectifier
    rectifier = PlanarMetricRectifier(src_points_px, dst_points_mm)
    
    # Calculate metric scale
    calculated_scale = rectifier.calculate_metric_scale()
    
    # The expected scale is 2 pixels/mm (400px/200mm = 2px/mm and 200px/100mm = 2px/mm)
    expected_scale = 2.0
    
    # Assert that the calculated scale matches the expected scale within 1% tolerance
    assert abs(calculated_scale - expected_scale) / expected_scale < 0.01, \
        f"Scale mismatch: expected {expected_scale}, got {calculated_scale}"


if __name__ == "__main__":
    pytest.main([__file__])